# Importing module
import mysql.connector
import datetime

# Creating connection object
server_db = mysql.connector.connect(
	host = "localhost",
	user = "root",
	password = "",
    database = "server"
)


def upload_file(file_tag, public_key, group,cipher_2,cipher_3,block_tags, metadata):
    file_exist = check_file_tag(file_tag)
    if file_exist==1:
        print('Init Subsequent Uplaod')
    else:
        insert_file(file_tag, public_key, group, cipher_2,cipher_3, block_tags, metadata)


def insert_file(file_tag, public_key, group,cipher_2,cipher_3, block_tags, metadata):
    print('Init File Upload')
    cursor = server_db.cursor()
    tag =  file_tag
    cursor.execute("create table if not exists hash_table (id INT AUTO_INCREMENT PRIMARY KEY, file_tag VARCHAR(255), is_group CHAR(1) DEFAULT 'N', group_no VARCHAR(1000), owner_table LONGTEXT, version_table VARCHAR(1000), cipher_2 LONGTEXT, cipher_3 LONGTEXT, block_tags LONGTEXT, metadata LONGTEXT)")
    owner_table_name = create_owner_table(public_key)
    group_name='N'
    # Create version table
    version_table = create_version_table(file_tag)
        # Create version table if not exists 
    if group =='N':
        insert_command = "insert into hash_table (file_tag, owner_table,version_table, cipher_2, cipher_3, block_tags, metadata) values (%s, %s, %s ,%s,%s,%s,%s)"
        insert_values = (tag,owner_table_name,version_table, cipher_2, cipher_3,block_tags, metadata)
        cursor.execute(insert_command, insert_values)
        
    else:
        timestamp = get_timestamp()
        group_name = 'group_'+timestamp
        insert_command = "insert into hash_table (file_tag, is_group, group_no ,owner_table,version_table, cipher_2, cipher_3,block_tags,  metadata) values (%s, %s, %s,%s,%s,%s,%s,%s,%s)"
        is_group = 'Y'
        insert_values= (tag,is_group, group_name,owner_table_name,version_table, cipher_2, cipher_3, block_tags,  metadata)
        cursor.execute(insert_command, insert_values)
        
    server_db.commit()
    print('File Uploaded')
    return group_name


def update(old_file_tag, new_file_tag, public_key,cipher_2,cipher_3, block_tags, metadata):
    version_table_name = get_version_table(old_file_tag)
    owner_table_name = get_owner_table_name(old_file_tag)
    cursor = server_db.cursor()
    if not check_access(old_file_tag,public_key):
        return -1 # No Access
    cursor.execute("insert into {} (file_tag) values (%s)".format(version_table_name),(new_file_tag,))
    is_group, group_no = get_group_det(old_file_tag)
    if is_group=='Y':
        insert_command = "insert into hash_table (file_tag, is_group, group_no ,owner_table,version_table,cipher_2,cipher_3, block_tags, metadata) values (%s, %s, %s,%s,%s,%s,%s,%s,%s)"
        is_group = 'Y'
        insert_values= (new_file_tag,is_group, group_no,owner_table_name,version_table_name,cipher_2,cipher_3, block_tags, metadata)
        cursor.execute(insert_command, insert_values)
    server_db.commit()
    return 1


def create_owner_table(public_key):
    cursor = server_db.cursor()
    timestamp = get_timestamp()
    owner_table_name = 'owner_table_'+timestamp
    cursor.execute("create table {} (id INT AUTO_INCREMENT PRIMARY KEY, public_key VARCHAR(1000))".format(owner_table_name))
    #cursor.execute(insert_command, insert_values)
    insert_command = "insert into {} (public_key) values (%s)".format(owner_table_name)
    cursor.execute(insert_command, (public_key,))        
    server_db.commit()
    return owner_table_name

def get_owner_table_name(file_tag):
    cursor = server_db.cursor()
    cursor.execute("select owner_table from hash_table where file_tag = %s",(file_tag,))
    myresult = cursor.fetchone()
    version_table_name = myresult[0]
    return version_table_name


def add_owner(file_tag, public_key):
    file_exist = check_file_tag(file_tag)
    if file_exist==1:
        owner_table_name = get_owner_table_name(file_tag)
        cursor = server_db.cursor()
        cursor.execute("insert into {} (public_key) values (%s)".format(owner_table_name),(public_key,))
        server_db.commit()
    else:
        return -1 # No file found


def delete_owner(file_tag, public_key):
    file_exist = check_file_tag(file_tag)
    if file_exist==1:
        owner_table_name = get_owner_table_name(file_tag)
        cursor = server_db.cursor()
        cursor.execute("delete from {} where public_key =%s".format(owner_table_name),(public_key,))
        server_db.commit()
        check_empty_owners(file_tag, owner_table_name)
    else:
        return -1 # No file found

def check_empty_owners(file_tag, owner_table_name):
    cursor = server_db.cursor()
    cursor.execute("select count(id) from {}".format(owner_table_name))
    count = cursor.fetchone()
    owner_count = count[0]
    if owner_count == 0:
        v_name = get_version_table(file_tag)
        cursor.execute("delete from hash_table where file_tag = %s", (file_tag,))
        cursor.execute("drop table {}".format(owner_table_name))
        cursor.execute("drop table {}".format(v_name))
        server_db.commit()


def create_version_table(file_tag):
    cursor = server_db.cursor()
    timestamp = get_timestamp()
    version_table_name = 'version_'+timestamp
    cursor.execute("create table {} (id INT AUTO_INCREMENT PRIMARY KEY, file_tag VARCHAR(1000))".format(version_table_name))
    #cursor.execute(insert_command, insert_values)
    insert_command = "insert into {} (file_tag) values (%s)".format(version_table_name)
    cursor.execute(insert_command, (file_tag,))        
    server_db.commit()
    return version_table_name

def get_version_table(file_tag):
    cursor = server_db.cursor()
    cursor.execute("select version_table from hash_table where file_tag = %s",(file_tag,))
    myresult = cursor.fetchone()
    version_table_name = myresult[0]
    return version_table_name

def get_timestamp():
    return str(datetime.datetime.now().timestamp()).replace('.','')

def check_file_tag(file_tag):
    cursor = server_db.cursor()
    cursor.execute("SELECT file_tag FROM hash_table where file_tag=%s",(file_tag,))
    myresult = cursor.fetchone()
    if myresult != None:
        return True #Duplicate File
    else:
        return False #New File

def get_latest_file_tag(file_tag):
    file_tag = str(file_tag)
    cursor = server_db.cursor()
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
    cursor = server_db.cursor()
    owner_table_name = get_owner_table_name(file_tag)
    cursor.execute("select count(id) from {} where public_key=%s".format(owner_table_name), (public_key,))
    myresult = cursor.fetchone()
    if myresult[0]==1:
        return True
    else:
        return False

def get_group_det(file_tag):
    cursor = server_db.cursor()
    cursor.execute("select is_group, group_no from hash_table where file_tag=%s",(file_tag,))
    myresult = cursor.fetchone()
    if myresult[0]=='N':
        return ('N','')
    else:
        return myresult

def get_ciphers(file_tag, public_key):
    access = check_access(file_tag, public_key)
    if access:
        cursor = server_db.cursor()
        cursor.execute("select cipher_2, cipher_3, block_tags, metadata from hash_table where file_tag=%s",(file_tag,))
        myresult = cursor.fetchone()
        cipher_2 = myresult[0]
        cipher_3 = myresult[1]
        block_tags = myresult[2]
        metadata = myresult[3]
        return (cipher_2, cipher_3, block_tags, metadata)
    else:
        return -1 #No Access
    
def get_meta(file_tag):
    cursor = server_db.cursor()
    cursor.execute("select metadata from hash_table where file_tag=%s",(file_tag,))
    myresult = cursor.fetchone()
    metadata = myresult[0]
    return metadata

def save_time(public_key, time_hash):
    cursor = server_db.cursor()
    cursor.execute("create table if not exists time_hash (id INT AUTO_INCREMENT PRIMARY KEY, public_key LONGTEXT, time_val LONGTEXT)")
    cursor.execute("insert into time_hash (public_key, time_val) values (%s,%s)", (public_key,time_hash))
    server_db.commit()

def get_time_hash(public_key):
    cursor = server_db.cursor()
    cursor.execute("select time_val from time_hash where public_key=%s",(public_key,))
    myresult = cursor.fetchone()
    if myresult != None:
        return myresult[0]
    else:
        return -1 # No time saved for Public Key
    
def save_block_vales(block_name, file_tag):
    cursor = server_db.cursor()
    cursor.execute("create table if not exists block_table (id INT AUTO_INCREMENT PRIMARY KEY, block_tag LONGTEXT, file_tag VARCHAR(255))")
    cursor.execute("insert into block_table (block_tag, file_tag) values(%s, %s)",(block_name, file_tag))


def check_block_exists(block_tag):
    cursor= server_db.cursor()
    cursor.execute("select id from block_table where block_tag=%s",(block_tag,))
    myresult = cursor.fetchone()
    if myresult!= None:
        return True
    else:
        return False

def get_block_values(file_tag):
    cursor = server_db.cursor()
    cursor.execute("select block_tags from hash_table where file_tag=%s",(file_tag,))
    myresult = cursor.fetchone()
    return myresult[0]

def get_file_tag_of_block(block_tag):
    cursor = server_db.cursor()
    cursor.execute("select file_tag from block_table where block_tag=%s",(block_tag,))
    myresult = cursor.fetchone()
    return myresult[0]


public_key = "PublicKey(0811894381714228791437715199125138441053188238781309785778539001753982230331889470118071352286003534767147063081280636475336316635332185292871419056936721970666851031602015612498812180909637220058492502528579123543268093376750727858037728412193990038676876669051466640315549098928940551851457399205667681378300824161, 65537)"
file_tag = "79289504320816749656312002797686303750053270932755277852798226741834612071265"
new_file_tag = "79289504320816749656312002797686303750053270932755277852798226741834612071265"
'''
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

get_ciphers(file_tag,public_key)


#save_time(public_key, file_tag)
get_time_hash(public_key)
#'''

#get_block_values(file_tag)