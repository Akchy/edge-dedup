# Importing module
import mysql.connector
import datetime

# Creating connection object
mydb = mysql.connector.connect(
	host = "localhost",
	user = "root",
	password = "",
    database = "server"
)

def upload_file(file_tag, public_key, group='N'):
    file_exist = check_file_tag(file_tag)
    if file_exist==1:
        print('Init Subsequent Uplaod')
    else:
        insert_file(file_tag, public_key, group)


def insert_file(file_tag, public_key, group):
    print('Init File Upload')
    cursor = mydb.cursor()
    tag =  file_tag
    cursor.execute("create table if not exists hash_table (id INT AUTO_INCREMENT PRIMARY KEY, file_tag VARCHAR(255), is_group CHAR(1) DEFAULT 'N', group_no VARCHAR(1000), owner_table LONGTEXT, version_table VARCHAR(1000))")
    owner_table_name = create_owner_table(public_key)
    # Create version table
    version_table = create_version_table(file_tag)
    print(version_table)
        # Create version table if not exists 
    if group =='N':
        insert_command = "insert into hash_table (file_tag, owner_table,version_table) values (%s, %s, %s)"
        insert_values = (tag,owner_table_name,version_table)
        cursor.execute(insert_command, insert_values)
        
    else:
        timestamp = get_timestamp()
        group_name = 'group_'+timestamp
        insert_command = "insert into hash_table (file_tag, is_group, group_no ,owner_table,version_table) values (%s, %s, %s,%s,%s)"
        is_group = 'Y'
        insert_values= (tag,is_group, group_name,owner_table_name,version_table)
        cursor.execute(insert_command, insert_values)
        
    mydb.commit()
    print('File Uploaded')


def update(old_file_tag, new_file_tag, public_key):
    version_table_name = get_version_table(old_file_tag)
    owner_table_name = get_owner_table_name(old_file_tag)
    cursor = mydb.cursor()
    if not check_access(old_file_tag,public_key):
        return -1 # No Access
    cursor.execute("insert into {} (file_tag) values (%s)".format(version_table_name),(new_file_tag,))
    is_group, group_no = get_group_det(old_file_tag)
    if is_group=='Y':
        insert_command = "insert into hash_table (file_tag, is_group, group_no ,owner_table,version_table) values (%s, %s, %s,%s,%s)"
        is_group = 'Y'
        insert_values= (new_file_tag,is_group, group_no,owner_table_name,version_table_name)
        cursor.execute(insert_command, insert_values)
    mydb.commit()
    return 1


def create_owner_table(public_key):
    cursor = mydb.cursor()
    timestamp = get_timestamp()
    owner_table_name = 'owner_table_'+timestamp
    cursor.execute("create table {} (id INT AUTO_INCREMENT PRIMARY KEY, public_key VARCHAR(1000))".format(owner_table_name))
    #cursor.execute(insert_command, insert_values)
    insert_command = "insert into {} (public_key) values (%s)".format(owner_table_name)
    cursor.execute(insert_command, (public_key,))        
    mydb.commit()
    return owner_table_name

def get_owner_table_name(file_tag):
    cursor = mydb.cursor()
    cursor.execute("select owner_table from hash_table where file_tag = %s",(file_tag,))
    myresult = cursor.fetchone()
    version_table_name = myresult[0]
    return version_table_name


def add_owner(file_tag, public_key):
    file_exist = check_file_tag(file_tag)
    if file_exist==1:
        owner_table_name = get_owner_table_name(file_tag)
        cursor = mydb.cursor()
        cursor.execute("insert into {} (public_key) values (%s)".format(owner_table_name),(public_key,))
        mydb.commit()
    else:
        return -1 # No file found


def delete_owner(file_tag, public_key):
    file_exist = check_file_tag(file_tag)
    if file_exist==1:
        owner_table_name = get_owner_table_name(file_tag)
        cursor = mydb.cursor()
        cursor.execute("delete from {} where public_key =%s".format(owner_table_name),(public_key,))
        mydb.commit()
        check_empty_owners(file_tag, owner_table_name)
    else:
        return -1 # No file found

def check_empty_owners(file_tag, owner_table_name):
    cursor = mydb.cursor()
    cursor.execute("select count(id) from {}".format(owner_table_name))
    count = cursor.fetchone()
    owner_count = count[0]
    if owner_count == 0:
        v_name = get_version_table(file_tag)
        cursor.execute("delete from hash_table where file_tag = %s", (file_tag,))
        cursor.execute("drop table {}".format(owner_table_name))
        cursor.execute("drop table {}".format(v_name))
        mydb.commit()


def create_version_table(file_tag):
    cursor = mydb.cursor()
    timestamp = get_timestamp()
    version_table_name = 'version_'+timestamp
    cursor.execute("create table {} (id INT AUTO_INCREMENT PRIMARY KEY, file_tag VARCHAR(1000))".format(version_table_name))
    #cursor.execute(insert_command, insert_values)
    insert_command = "insert into {} (file_tag) values (%s)".format(version_table_name)
    cursor.execute(insert_command, (file_tag,))        
    mydb.commit()
    return version_table_name

def get_version_table(file_tag):
    cursor = mydb.cursor()
    cursor.execute("select version_table from hash_table where file_tag = %s",(file_tag,))
    myresult = cursor.fetchone()
    version_table_name = myresult[0]
    return version_table_name

def get_timestamp():
    return str(datetime.datetime.now().timestamp()).replace('.','')

def check_file_tag(file_tag):
    cursor = mydb.cursor()
    cursor.execute("SELECT file_tag FROM hash_table where file_tag=%s",(file_tag,))
    myresult = cursor.fetchone()
    if myresult != None:
        return 1 #Duplicate File
    else:
        return 0 #New File

def get_latest_file_tag(file_tag):
    file_tag = str(file_tag)
    cursor = mydb.cursor()
    file_exist = check_file_tag(file_tag)
    if file_exist==1:
        cursor.execute("SELECT version_table FROM hash_table where file_tag=%s",(file_tag,))
        version_table = cursor.fetchone()
        version_table_name = version_table[0]
        cursor.execute("SELECT file_tag FROM {} order by id desc limit 1".format(version_table_name))
        latest_tag_list = cursor.fetchone()
        latest_file_tag = latest_tag_list[0]
        if latest_file_tag != file_tag:
            return latest_tag_list
        else:
            return 0 # Same file
    else:
        return -1 # No file found
    
def check_access(file_tag,public_key):
    cursor = mydb.cursor()
    owner_table_name = get_owner_table_name(file_tag)
    cursor.execute("select count(id) from {} where public_key=%s".format(owner_table_name), (public_key,))
    myresult = cursor.fetchone()
    if myresult[0]==1:
        return True
    else:
        return False

def get_group_det(file_tag):
    cursor = mydb.cursor()
    cursor.execute("select is_group, group_no from hash_table where file_tag=%s",(file_tag,))
    myresult = cursor.fetchone()
    if myresult[0]=='N':
        return ('N','')
    else:
        return myresult

'''
public_key = "PublicKey(1510856045871991099461062366966773242040587774291150808567196749515647261994583466034466236092427883017102311971032367607967106870044544473378462108167492238574561256385306847869581764606954295267464370702638991370748037790760894195692666823244646249641362973234990065292745326457163344292839621322258953903474872999, 65537)"
file_tag = "79289504320816749656312002797686303750053270932755277852798226741834612071263"
new_file_tag = "79289504320816749656312002797686303750053270932755277852798226741834612071265"

#insert_file(file_tag,public_key,'N')
#x = get_owner_list(file_tag)
#check_file_tag(file_tag)
#upload_file(file_tag, public_key,'Y')
#print(x)
#delete_owner(file_tag,public_key)
#x = get_latest_file_tag(file_tag)
#print(x)
#delete_owner(file_tag, public_key)
#get_group_det(file_tag)

#x =update(file_tag, new_file_tag, public_key)
#print(x)
'''
