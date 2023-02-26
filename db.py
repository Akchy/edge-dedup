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

def insert_file(file_tag, public_key, group='N'):

    cursor = mydb.cursor()
    tag =  file_tag
    cursor.execute("create table if not exists hash_table (id INT AUTO_INCREMENT PRIMARY KEY, file_tag VARCHAR(255), is_group CHAR(1) DEFAULT 'N', group_no VARCHAR(1000), owner_list LONGTEXT, version_table VARCHAR(1000))")
    update_owner(file_tag,public_key)
    owner_list = get_owner_list(file_tag)
    # Create version table
    version_table = create_version_table(file_tag)
        
        # Create version table if not exists 
    if group =='N':
        insert_command = "insert into hash_table (file_tag, owner_list,version_table) values (%s, %s, %s)"
        insert_values = (tag,owner_list,version_table)
        cursor.execute(insert_command, insert_values)
        
    else:
        timestamp = get_timestamp()
        group_name = 'group_'+timestamp
        insert_command = "insert into hash_table (file_tag, is_group, group_no ,owner_list,version_table) values (%s, %s, %s,%s,%s)"
        is_group = 'Y'
        insert_values= (tag,is_group, group_name,owner_list,version_table)
        cursor.execute("create table if not exists hash_table (id INT AUTO_INCREMENT PRIMARY KEY, file_tag VARCHAR(255), is_group CHAR(1) DEFAULT 'N', group_no VARCHAR(1000), owner_list LONGTEXT, version_table VARCHAR(1000))")
        cursor.execute(insert_command, insert_values)
        
    mydb.commit()


def get_owner_list(file_tag):
    #Get Owner List
    mycursor = mydb.cursor()
    mycursor.execute("SELECT owner_list FROM hash_table where file_tag={}".format(file_tag))
    myresult = mycursor.fetchone()
    #return myresult
    if myresult != None:
        return(myresult[0])
    else:
        return -1

def update_owner(file_tag, public_key):
    val = get_owner_list(file_tag)
    if val == -1:
        o_list = []
    else:
        o_list_string = str(val)
        o_list = list(o_list_string.split("-"))
    o_list.append(public_key)
    o_list_string = '-'.join(o_list)
    mycursor = mydb.cursor()
    mycursor.execute("update hash_table set owner_list=%s where file_tag=%s", (o_list_string,file_tag))
    #return myresult
    mydb.commit()

def create_version_table(file_tag):
    cursor = mydb.cursor()
    timestamp = get_timestamp()
    version_table_name = 'version_'+timestamp
    cursor.execute("create table {} (id INT AUTO_INCREMENT PRIMARY KEY, file_tag VARCHAR(255))".format(version_table_name))
    #cursor.execute(insert_command, insert_values)
    insert_command = "insert into {} (file_tag) values ({})".format(version_table_name,file_tag)
    cursor.execute(insert_command)        
    mydb.commit()
    return version_table_name

def get_timestamp():
    return str(datetime.datetime.now().timestamp()).replace('.','')

def create_gorup_table():
    
    return 

public_key = "PublicKey(1510856045871991099461062366966773242040587774291150808567196749515647261994583466034466236092427883017102311971032367607967106870044544473378462108167492238574561256385306847869581764606954295267464370702638991370748037790760894195692666823244646249641362973234990065292745326457163344292839621322258953903474872999, 65537)"
file_tag = "79289504320816749656312002797686303750053270932755277852798226741834612071265"
insert_file(file_tag,public_key)
#get_owner_list(file_tag)
'''
cursor = mydb.cursor()
name = 'abc_24'
cursor.execute("create table {} (id int)".format(name))
#get_owner_list(file_tag)

#'''