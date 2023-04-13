import db
from mod.modulo_hash import *


prime1 = 85317060646768443274134832250229019514319591632920326205376943415602602947019

def check_latest(file_name, public_key):
    file_tag = modulo_hash_file(file_name, prime1)
    latest_file_tag = db.get_latest_file_tag(file_tag)
    if latest_file_tag >0:
        print('New version')
        #init_donwload(latest_file_tag, public_key)
    elif latest_file_tag ==0:
        print('Same version')
    elif latest_file_tag==-1:
        print('No File Found\nInit Upload')


#update('test.txt')