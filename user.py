# Here's the code for user
import rsa
import edge
import server
from mod.enc.aes import *
from mod.modulo_hash import *
from mod.enc.sarce import get_rce_key
from mod.divide_files import merge_blocks
from mod.enc.rsa_keys import generate_keys, rsa_decypt
from mod.divide_files import divide_file_by_size

prime1 = 85317060646768443274134832250229019514319591632920326205376943415602602947019
prime2 = 154813591145766135381307408100320581872727279802381926251921153367959654726445983463789452039725321237307989748816194466520946981165617567414284940369508252295621408568741594522799840574828305266316028435844847717554430653505159371815836799626994815914862273363768236564919004629159198309175554423687355013493
temp = 11037229919296391044771832604060314898870002775346764076594975490923595002795272111869578867022764684137991653602919487206273710450289426260391664067192117
user_input_folder_name = 'files/blocks/'
user_output_folder_name = 'files/encrypt_blocks/'
user_down_input_folder_name = 'files/edge_decrypt_blocks/'
user_down_output_folder_name = 'files/dencrypt_blocks/'
user_sub_input_folder_name = 'subs_blocks/'
file_size = 1024

iv = b"\x80\xea\xacbU\x01\x0e\tG\\4\xefQ'\x07\x92"
if not os.path.exists('files'):
        os.mkdir('files')
if not os.path.exists('datas'):
        os.mkdir('datas')

def user_upload(file_name, group,public_key, private_key,is_update='N', old_file_tag=''):
    file_tag = get_file_tag(file_name)
    # RCE Key Generation
    edge_rce_key = edge.get_edge_rce_key()
    str_rce_key = get_rce_key(file_tag,edge_rce_key)
    rce_key = bytes(str_rce_key[0:24],'utf-8')
    file_exists = edge.check_file_tag_exists_server(file_tag)
    if is_update=='N' and file_exists == True:
        subs_upload(file_name, file_tag,public_key,private_key)
    else:
        
        file_count,cipher_2,cipher_3, cuckoo_blocks=encrypt_blocks(file_name, file_tag, rce_key, public_key, private_key)
        metadata = [file_name,file_count]
        cipher_2_list= '-'.join(str(c) for c in cipher_2)
        cuckoo_blocks_list= '-'.join(str(c) for c in cuckoo_blocks)
        group_name = edge.upload_to_edge(file_tag, str(public_key), group, file_count,cipher_2_list,str(cipher_3), cuckoo_blocks_list, str(metadata), is_update, old_file_tag)

        #save group name in a file
        with open('datas/group_name.txt', 'a+') as file:
            file.write('\n\ngroup_name= {}'.format(group_name))

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
        aes_encrypt_file(bytes_K, iv, user_input_folder_name, user_output_folder_name,block_name)
        bytes_cipher = aes_encrypt_byte(rce_key,mod)
        int_cipher = int.from_bytes(bytes_cipher,'big')
        cipher_2.append(int_cipher)
    int_rce_key = int.from_bytes(rce_key,'big')
    cipher_3 = int_rce_key ^ prime2
    
    # Saving User's Public and Private keys in a file.
    with open('datas/rsa.txt','w+') as file:
        file.write('\n\npublic= {} \nprivate= {}'.format(public_key,private_key))

    with open('datas/file_tag.txt', 'a+') as file:
        file.write('\n\nfile_tag= {}'.format(file_tag))

    with open('datas/metadata.txt', 'a+') as file:
        file.write('\n\nfile_name= {}\nfile_count= {}'.format(file_name, file_count))

    with open('datas/ciphers.txt', 'a+') as file:
        file.write('\n\ncipher_2= {}\ncipher_3= {}'.format(cipher_2,cipher_3))

    return file_count, cipher_2, cipher_3, cuckoo_blocks

def user_download(file_name,public_key):
    file_tag = get_file_tag(file_name)
    val_tag = check_for_update(file_name,'N')
    if val_tag!=0 and val_tag !=-1:
        val =edge.download_from_edge(val_tag[0], public_key)
    else:
        val =edge.download_from_edge(file_tag, public_key)
    if val == -1:
        print('No Access to the file')
        return -1
    cipher_2_list, cipher_3, metadata =val
    save_file_name, file_count = metadata
    save_file_name =save_file_name[2:-1]
    cipher_2_str = cipher_2_list.split('-')
    file_count = int(file_count[:-1])
    cipher_3_int = int(cipher_3)
    int_rce_key = cipher_3_int ^prime2
    rce_key = int_rce_key.to_bytes(24,'big')
    for i in range (1,file_count):
        cipher_2_int = int(cipher_2_str[i-1])
        byte_cipher = cipher_2_int.to_bytes(64,'big')
        block_key = aes_decrypt_byte(rce_key,byte_cipher)
        file_name = 'block{}.bin'.format(i)
        aes_decrypt_file(block_key, iv, user_down_input_folder_name, user_down_output_folder_name,file_name)
    save_file_name = 'downloaded_'+save_file_name
    merge_blocks(user_down_output_folder_name,save_file_name)
    print('File downloaded and saved under the name: ',save_file_name)

def subs_upload(file_name, file_tag, public_key, private_key):
    
    value = edge.check_access_server(file_tag,public_key)
    if not value:
        print("Same Person")
        return 0
    print('Different Person')
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
    
    val = edge.blocks_to_server_cuckoo_server(file_tag, block_keys, public_key)
    if val != -1:
        time_dec = rsa_decypt(private_key,val)
        x = edge.check_time_hash_server(file_tag, public_key, time_dec)
    #'''

def check_for_update(file_name, display='Y'):
    #check the server for update
    file_tag = get_file_tag(file_name)
    val = edge.check_fo_update_server(file_tag)
    if display=='N':
        return val
    if val==0:
        print('Same No Update')
    elif val == -1:
        print('No File in server, Upload as a New File')
    else:
        print('A new version of the file is available and the file tag is mentioned below: \nNew File Tag: {}'.format(val[0]))
        print('\nPlease use the below mentioned file tag while updating: \nOld File Tag: {}\n'.format(file_tag))

#public_key, private_key = generate_keys()
public_key = rsa.PublicKey(1619750136252618332977235896406521010807545517612785245212451483502410574525825995344209832503413765595553218797211650165668796624501025356465915373792919645936327492224490288645578575138223278878781813799762886037191557934865815503565013998614220110374116025960745945204394432266977381294688936349494087274295987083, 65537)
private_key = rsa.PrivateKey(1619750136252618332977235896406521010807545517612785245212451483502410574525825995344209832503413765595553218797211650165668796624501025356465915373792919645936327492224490288645578575138223278878781813799762886037191557934865815503565013998614220110374116025960745945204394432266977381294688936349494087274295987083, 65537, 1030691669318750359951625319862690475818347967117902605872939930367594308397554381247838360695330336552349907433970389960768509782742058080789448232712325826281082261178632239073798253718751096103441456539354111286400036129262946954889075051792123457429342509369899192140299157753644374884936706624123295044143642185, 144316483646245528065267241335886041264166327522302219260632995815227677664448673850105699878958127212618068955859752072987245918861275831575505446408281521548720709797, 11223597577550573967916132102918873794347730871873978637357031959131200754447345444825878496219616432817134464015955214999041127472681083882349565039)
#public_key= rsa.PublicKey(1512831018278585743841472696740207789602100915654757895338084051019981320336842454667198778630112787313780098742495247885756974310935334921414696040923269923378353222183085473799462635687460593000951865522396872717298868278903520291825340358641335850759829062254526135031854570310876145080522323534956208489004610857, 65537) 
#private_key= rsa.PrivateKey(1512831018278585743841472696740207789602100915654757895338084051019981320336842454667198778630112787313780098742495247885756974310935334921414696040923269923378353222183085473799462635687460593000951865522396872717298868278903520291825340358641335850759829062254526135031854570310876145080522323534956208489004610857, 65537, 1296122020314086865907118886266779486066929586540412302445001775801775045479551505059867620142853699358857420453978144766122470521761876810084589895631526384627894119493557656871268193012699663523477134432434019931649558069860282557718131802344357259907672054159038277642546515992580505422152487417519344873374751953, 210107718007673478827841822507130275005760128893000947010995116566391878871457378432327937171500421528217531480977310848366445709997193856230927826781335188364258139741, 7200263905694957246674054940590485390626170401196093626142230160532627252925841182458429597636885243354582825680728031714977538875796565460079938877)

file_name = 'ieee.png'
is_group = 'Y'
is_update= 'N'
old_file_tag = '79289504320816749656312002797686303750053270932755277852798226741834612071265'
#user_upload(file_name,is_group, public_key, private_key,is_update, old_file_tag)

user_download(file_name, public_key)
#user_update('test.txt', public_key, '79289504320816749656312002797686303750053270932755277852798226741834612071265')
#check_for_update('test.txt',public_key)