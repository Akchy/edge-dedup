from mod.modulo_hash import *
from mod.random_key import *
from mod.gen_rsa_keys import generate_keys
import random


def RCE():
    #Generate File Tag
    filename = 'test.txt'
    p = 4299131183

    file_tag = modulo_hash_file(filename,p)
    #RCE key steps

    #print('file tag: ' + str(file_tag))


    d,e,N = generate_keys()
    
    #Random Number
    #print('\nd: '+str(d)+ '\ne: '+str(e)+ '\nN: '+str(N))
    r = random.randint(1, N) # here the N is set by Public variale of RSA
    
    #User sends x to edge
    x = modulo_hash_file(filename,p)*(r**e)%N


    #Edge cmoputes the following
    y = (x^d)%N

    #Then user calculates z
    z = (y*r^(-1))%N

    print('\nX: '+ str(x) + '\nY: ' + str(y) + ' \nZ: ' + str(z) )
    #Then can verify the following

    #Generate Random Number
    l = random_num_gen()

    #RCE Key K_f
    K_f = (l,z)

    #Print RCE
    #print('\nK: ',K_f)

    #Return rce key
    return K_f