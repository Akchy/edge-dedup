import db

def check_file_tag_exists(file_tag):
    exists = db.check_file_tag(file_tag)
    return exists

def upload_to_server(file_tag, public_key, group,cipher_2,cipher_3, metadata):
    group_name = db.upload_file(file_tag, public_key, group,cipher_2,cipher_3, metadata)
    return group_name


def download_from_server(file_tag, public_key):
    val = db.get_ciphers(file_tag, public_key)
    if val == -1 :
        return -1
    cipher_2, cipher_3, metadata =val
    return cipher_2, cipher_3, metadata
   