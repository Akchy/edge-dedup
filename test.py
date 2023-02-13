# declaring an integer value
integer_val = 15414534062424964199044617770449011887

# converting int to bytes with length
# of the array as 2 and byter order as big
bytes_val = integer_val.to_bytes(32, 'big')

byte_val = b'\xc9\xe4L\xbbd\xb3^\xf8\x93\x93\xba\xbb\xcb\xd2M(otQG\xc6\x83\xeb \x8a[p;\x9e%\xe2\x12'
int_val = int.from_bytes(byte_val, "big")
# printing integer in byte representation
print(int_val)
