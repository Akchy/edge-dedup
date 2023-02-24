import random
file_tags = [ 79289504320816749656312002797686303750053270932755277852798226741834612071265]

file_tag =  79289504320816749656312002797686303750053270932755277852798226741834612071265
file_count = 4

if file_tag not in file_tags:
    print('Its a new file, upload it please.')
else:
    count=0
    blocks = []
    print('duplicate')
    while count!=3:
        num = random.randint(1,file_count)
        if num not in blocks:
            blocks.append(num)
            count+=1
    #send these block numbers to User
    
        
    
