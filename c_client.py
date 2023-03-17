import socket

# Here's the code for user
import rsa
from mod.enc.aes import *
from mod.modulo_hash import *
from mod.enc.sarce import get_rce_key
from mod.divide_files import merge_blocks
from mod.enc.rsa_keys import generate_keys, rsa_decypt
from mod.divide_files import divide_file_by_size

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT-OUT"
EDGE = "10.0.0.2"
ADDR = (EDGE, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

prime1 = 85317060646768443274134832250229019514319591632920326205376943415602602947019
prime2 = 154813591145766135381307408100320581872727279802381926251921153367959654726445983463789452039725321237307989748816194466520946981165617567414284940369508252295621408568741594522799840574828305266316028435844847717554430653505159371815836799626994815914862273363768236564919004629159198309175554423687355013493
temp = 11037229919296391044771832604060314898870002775346764076594975490923595002795272111869578867022764684137991653602919487206273710450289426260391664067192117
user_input_folder_name = 'files/blocks/'
user_output_folder_name = 'files/encrypted_blocks_'
user_down_input_folder_name = 'files/edge_decrypted_blocks_'
user_down_output_folder_name = 'files/decrypted_blocks_'
user_sub_input_folder_name = 'subs_blocks/'
file_size = 1024

iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92"
if not os.path.exists('files'):
        os.mkdir('files')

def __send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    if msg_length > 1024:
        #print(f'large_text-{msg_length}')
        __send(f'large_text-{msg_length}')
        client.sendall(message)
    else:
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        #print(f'msg: {msg}')
        client.send(send_length)
        client.send(message)

def split_message(message,chunk_size):
    chunks = []
    for i in range(0, len(message), chunk_size):
        chunks.append(message[i:i+chunk_size])
    return chunks

def send_text(key, str,large='N'):
    list = [key,str]
    l_str = '-'.join(list)
    #print(f'send: {l_str}')
    __send(l_str)
    #list_string=client.recv(1024).decode(FORMAT)
    if large=='N':
        list_string =client.recv(2048).decode(FORMAT)
    else:
        msg_len_str = client.recv(HEADER).decode(FORMAT)
        msg_len = int(msg_len_str)
        list_string = get_large_text(msg_len)
    #print(f'return: {list_string}')
    if large=='Y':
        return list_string
    elif list_string:
        list = list_string.split('-/')
        val = list[1]
        return val

def get_large_text(str_len):
    large = ''
    v = True
    l = int(str_len)
    while v:
        data = client.recv(1024).decode(FORMAT)
        large +=data
        l = l-len(data)
        if l<=0:
            v = False
    return large    

def send_file(filename):
    send_file_name_list = ['send_file', filename]
    send_file_name_string = '-'.join(send_file_name_list)
    __send(send_file_name_string)

    with open(filename, 'rb') as f:
        data = f.read()
        #print(f'leng: {len(data)}')
        __send(f'len-{len(data)}')
        client.sendall(data)
 
def get_file(filename):
    # get_file_name_list = ['get_file', filename]
    # get_file_name_string = '-'.join(get_file_name_list)
    # __send(get_file_name_string)

    # receive file contents from server and save to disk

    msg_length = client.recv(HEADER).decode(FORMAT)
    msg_length = int(msg_length)
    msg = client.recv(msg_length).decode(FORMAT)
    #print(f'file_name: {filename}')
    li = msg.split('-')
    file_size = int(li[1]) 
    with open(filename, 'wb') as f:
        l = file_size
        v = True
        while v:
            data = client.recv(1024)
            #print(f'l: {l} data: {data}')
            f.write(data)
            l = l - len(data)
            if l<=0:
                v=False
def send_folder(folder_name, file_tag):
    files = os.listdir(folder_name)
    key = 'folder_share'
    l = str(len(files))
    li = [l,str(file_tag)]
    li_str = '+'.join(li)
    command = key+'-'+li_str
    __send(command)
    for file in files:
        file_path = folder_name+file
        send_file(file_path)
        x = client.recv(13).decode(FORMAT)

def get_folder_from_edge(file_count):
    for i in range(1,file_count):
        #print(f'loop: {i}')
        msg_length = client.recv(HEADER).decode(FORMAT)
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        l = msg.split('-')
        file_name = l[1]
        get_file(file_name)
        x = client.send('Received File'.encode(FORMAT))
    

def user_upload(file_name,public_key, private_key,group='N',is_update='N', old_file_tag=''):
    file_tag = get_file_tag(file_name)
    # RCE Key Generation
    command = 'get_edge_rce_key'
    arg = 'key'
    int_edge_rce_key = int(send_text(command,arg))
    edge_rce_key = int_edge_rce_key.to_bytes(16, 'big')
    #edge_rce_key = edge.get_edge_rce_key()
    str_rce_key = get_rce_key(file_tag,edge_rce_key)
    rce_key = bytes(str_rce_key[0:24],'utf-8')
    command = 'check_file_tag_exists'
    arg = str(file_tag)
    file_exists_str = send_text(command,arg)
    if file_exists_str == 'True':
        file_exists = True
    else:
        file_exists = False
    #file_exists = edge.check_file_tag_exists_server(file_tag)
    if is_update=='N' and file_exists == True:
        subs_upload(file_name, file_tag,public_key,private_key)
    else:
        file_count,cipher_2,cipher_3, cuckoo_blocks=encrypt_blocks(file_name, file_tag, rce_key, public_key, private_key)
        metadata = [file_name,file_count]
        cipher_2_list= '/'.join(str(c) for c in cipher_2)
        cuckoo_blocks_list= '/'.join(str(c) for c in cuckoo_blocks)
        command = 'upload_to_edge'
        l = [str(file_tag),str(public_key), group, str(file_count),cipher_2_list,str(cipher_3), cuckoo_blocks_list, str(metadata), is_update, str(old_file_tag)]
        s = '+'.join(l)
        arg = s
        send_text(command,arg)
        #edge.upload_to_edge(file_tag, str(public_key), group, file_count,cipher_2_list,str(cipher_3), cuckoo_blocks_list, str(metadata), is_update, old_file_tag)
        
        print('User: File Uploaded\nPlease save the file tag mentioned below: \nFile Tag: {}'.format(file_tag))

def get_file_tag(file_name):
    return modulo_hash_file(file_name,prime1)

def encrypt_blocks(file_name, file_tag, rce_key, public_key, private_key):
    file_count=divide_file_by_size(file_name, file_size, user_input_folder_name)
    block_keys = []
    cuckoo_blocks = []
    cipher_2 = []
    for i in range (1,file_count):
        block_name = 'block{}.bin'.format(i)
        block_path = user_input_folder_name+block_name
        mod = modulo_hash_file(block_path,prime1)
        block_keys.append(mod)
        cuckoo_mod = modulo_hash_file(block_path,prime2)
        cuckoo_blocks.append(cuckoo_mod)
        bytes_K = mod.to_bytes(32, 'big')
        user_output_folder_name1 = user_output_folder_name + str(file_tag)+'/'
        aes_encrypt_file(bytes_K, iv, user_input_folder_name, user_output_folder_name1,block_name)
        bytes_cipher = aes_encrypt_byte(rce_key,mod)
        int_cipher = int.from_bytes(bytes_cipher,'big')
        cipher_2.append(int_cipher)
    send_folder(user_output_folder_name1, file_tag)
    int_rce_key = int.from_bytes(rce_key,'big')
    cipher_3 = int_rce_key ^ prime2
    
    # Saving User's Public and Private keys in a file.
    with open('files/rsa.txt','w+') as file:
        file.write('\n\npublic= {} \nprivate= {}'.format(public_key,private_key))
    return file_count, cipher_2, cipher_3, cuckoo_blocks

def user_download(file_tag,public_key):
    user_down_input_folder_name1 = user_down_input_folder_name + str(file_tag)+'/'
    if not os.path.exists(user_down_input_folder_name1):
        os.mkdir(user_down_input_folder_name1)
    val_tag = check_for_update(file_tag,'N')
    if val_tag!='0' and val_tag !='-1':
        tag = val_tag        
    else:
        tag = file_tag
    command = 'download_from_edge'
    l = [str(tag),str(public_key)]
    s = '+'.join(l)
    arg = s
    value_str = send_text(command,arg,'Y')    
    #val =edge.download_from_edge(tag, public_key)
    if value_str == '-1':
        print('User: No Access to the file')
        return -1
    val_list = value_str.split('*')
    cipher_2_list = val_list[0] 
    cipher_3 = val_list[1]
    metadata = val_list[2]
    save_file_name, file_count = metadata.split(',')
    save_file_name =save_file_name[2:-1]
    cipher_2_str = cipher_2_list.split('/')
    cipher_3_int = int(cipher_3)
    int_rce_key = cipher_3_int ^prime2
    rce_key = int_rce_key.to_bytes(24,'big')
    file_count = int(file_count[:-1])

    command = 'download_folder_from_edge'
    arg = str(tag)
    l = [command,arg]
    l_str = '-'.join(l)
    __send(l_str)
    #print('getting files')
    get_folder_from_edge(file_count)
    #print('done')
    for i in range (1,file_count):
        #get file
        cipher_2_int = int(cipher_2_str[i-1])
        byte_cipher = cipher_2_int.to_bytes(64,'big')
        block_key = aes_decrypt_byte(rce_key,byte_cipher)
        file_name = 'block{}.bin'.format(i)
        user_down_output_folder_name1 = user_down_output_folder_name + str(tag)+'/'
        aes_decrypt_file(block_key, iv, user_down_input_folder_name1, user_down_output_folder_name1,file_name)
    save_file_name = 'downloaded_'+save_file_name
    merge_blocks(user_down_output_folder_name1,save_file_name)
    print('User: File downloaded and saved under the name: ',save_file_name)

def subs_upload(file_name, file_tag, public_key, private_key):
    command = 'check_access'
    l = [str(file_tag),str(public_key)]
    s = '+'.join(l)
    arg = s
    value_str = send_text(command,arg)
    #value = edge.check_access_server(file_tag,public_key)
    #print(f'check value: {value_str}')
    if value_str =='False':
    #if value ==False:
        print("User: Same Person")
        return 0
    else:
        value = [int(i) for i in value_str.split('*')]
    print('User: Different Person')
    #'''

    if not os.path.exists('subs_blocks'):
        os.mkdir('subs_blocks')
    block_list = value
    _=divide_file_by_size(file_name, file_size, user_sub_input_folder_name)
    block_keys = []
    for i in block_list:
        file_name = 'block{}.bin'.format(i)
        file_path = user_sub_input_folder_name+file_name
        mod = modulo_hash_file(file_path,prime2)
        block_keys.append(mod)
    command = 'blocks_to_server_cuckoo'
    block_keys_str = '/'.join(str(b) for b in block_keys)
    l = [str(file_tag),block_keys_str,str(public_key)]
    s = '+'.join(l)
    arg = s
    val = send_text(command,arg)
    li = val.split('*')
    b_len = int(li[0])
    b_int = int(li[1])
    cipher = b_int.to_bytes(b_len,'big')
    #val = edge.blocks_to_server_cuckoo_server(file_tag, block_keys, public_key)
    if val != '-1':
        time_dec = rsa_decypt(private_key,cipher)
        command = 'check_time_hash'
        l = [str(file_tag),str(public_key),time_dec]
        s = '+'.join(l)
        arg = s
        x = send_text(command,arg)
        #x = edge.check_time_hash_server(file_tag, public_key, time_dec)
    #'''

def check_for_update(file_tag, display='Y'):
    command = 'check_for_update'
    arg = str(file_tag)
    val = send_text(command,arg)
    #val = edge.check_fo_update_server(file_tag)
    if display=='N':
        return val
    if val=='0':
        print('User: Same No Update')
    elif val == '-1':
        print('User: No File in server, Upload as a New File')
    else:
        print('User: A new version of the file is available and the file tag is mentioned below: \nNew File Tag: {}'.format(val))
        print('\nUser: Please use the below mentioned file tag while updating: \nOld File Tag: {}\n'.format(file_tag))

def add_user(file_name, public_key, new_public_key):
    file_tag = get_file_tag(file_name)
    command = 'add_user'
    l = [str(file_tag),str(public_key), str(new_public_key)]
    s = '+'.join(l)
    arg = s
    val = send_text(command,arg)
    #val = edge.add_user_server(file_tag, public_key, new_public_key)
    if val =='1':
        print('User: User Added Successfully')
    elif val == '-1':
        print('User: No File Found')
    elif val == '-2':
        print('User: No Access Found')
    elif val == '-3':
        print('User: User is not an Admin')
    elif val == '-4':
        print('User: New User Already Present')

def delete_user(file_name, public_key, new_public_key):
    file_tag = get_file_tag(file_name)
    command = 'delete_user'
    l = [str(file_tag),str(public_key), str(new_public_key)]
    s = '+'.join(l)
    arg = s
    val = send_text(command,arg)
    #val = edge.delete_user_server(file_tag, public_key, new_public_key)
    if val ==1:
        print('User: User Deleted Successfully')
    elif val == '-1':
        print('User: No File Found')
    elif val == '-2':
        print('User: No Access Found')
    elif val == '-3':
        print('User: User is not an Admin')
    elif val == '-4':
        print('User: New User Already Deleted')
    

#public_key, private_key = generate_keys()
public_key = rsa.PublicKey(1619750136252618332977235896406521010807545517612785245212451483502410574525825995344209832503413765595553218797211650165668796624501025356465915373792919645936327492224490288645578575138223278878781813799762886037191557934865815503565013998614220110374116025960745945204394432266977381294688936349494087274295987083, 65537)
private_key = rsa.PrivateKey(1619750136252618332977235896406521010807545517612785245212451483502410574525825995344209832503413765595553218797211650165668796624501025356465915373792919645936327492224490288645578575138223278878781813799762886037191557934865815503565013998614220110374116025960745945204394432266977381294688936349494087274295987083, 65537, 1030691669318750359951625319862690475818347967117902605872939930367594308397554381247838360695330336552349907433970389960768509782742058080789448232712325826281082261178632239073798253718751096103441456539354111286400036129262946954889075051792123457429342509369899192140299157753644374884936706624123295044143642185, 144316483646245528065267241335886041264166327522302219260632995815227677664448673850105699878958127212618068955859752072987245918861275831575505446408281521548720709797, 11223597577550573967916132102918873794347730871873978637357031959131200754447345444825878496219616432817134464015955214999041127472681083882349565039)
new_public_key= rsa.PublicKey(1512831018278585743841472696740207789602100915654757895338084051019981320336842454667198778630112787313780098742495247885756974310935334921414696040923269923378353222183085473799462635687460593000951865522396872717298868278903520291825340358641335850759829062254526135031854570310876145080522323534956208489004610857, 65537) 
new_private_key= rsa.PrivateKey(1512831018278585743841472696740207789602100915654757895338084051019981320336842454667198778630112787313780098742495247885756974310935334921414696040923269923378353222183085473799462635687460593000951865522396872717298868278903520291825340358641335850759829062254526135031854570310876145080522323534956208489004610857, 65537, 1296122020314086865907118886266779486066929586540412302445001775801775045479551505059867620142853699358857420453978144766122470521761876810084589895631526384627894119493557656871268193012699663523477134432434019931649558069860282557718131802344357259907672054159038277642546515992580505422152487417519344873374751953, 210107718007673478827841822507130275005760128893000947010995116566391878871457378432327937171500421528217531480977310848366445709997193856230927826781335188364258139741, 7200263905694957246674054940590485390626170401196093626142230160532627252925841182458429597636885243354582825680728031714977538875796565460079938877)

file_name = 'test.txt'
group = 'Y'
update= 'Y'
old_tag = '79289504320816749656312002797686303750053270932755277852798226741834612071265'
file_tag = '62083022736372406286878543231345933678695456481173225593791197450501253020534'
#user_upload(file_name, public_key, private_key,group=group,is_update=update,old_file_tag=old_tag)

user_download(file_tag, public_key)
#user_update('test.txt', public_key, '79289504320816749656312002797686303750053270932755277852798226741834612071265')
#check_for_update(old_tag,public_key)

#delete_user(file_name, public_key, new_public_key)
#add_user(file_name, public_key, new_public_key)
__send(DISCONNECT_MESSAGE)
client.close()