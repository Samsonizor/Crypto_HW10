from bitstring import *

# Define dictionaries used for substititutions and pemutations
# substitution dictionary for encryption
sub_dict_encrypt = {
    '0': 'e',
    '1': '4',
    '2': 'd',
    '3': '1',
    '4': '2',
    '5': 'f',
    '6': 'b',
    '7': '8',
    '8': '3',
    '9': 'a',
    'a': '6',
    'b': 'c',
    'c': '5',
    'd': '9',
    'e': '0',
    'f': '7',
}

# substitution dictionary for decryption, an inverse of the disctionary for encryption
sub_dict_decrypt = {v: k for k, v in sub_dict_encrypt.items()}

# permutation dictionary for encryption
perm_dict_encrypt = {
    1: 1,
    2: 5,
    3: 9,
    4: 13,
    5: 2,
    6: 6,
    7: 10,
    8: 14,
    9: 3,
    10: 7,
    11: 11,
    12: 15,
    13: 4,
    14: 8,
    15: 12,
    16: 16,
}
# permutation dictionary for decryption, an inverse of the dictionary for encryption
perm_dict_decrypt = {v: k for k, v in perm_dict_encrypt.items()}

def get_keys(master_key: BitArray, num_keys: int):
    """
    Generate keys from the master key using the key scheduling algorithm shown in Stinson
    :param master_key: master keys which the round keys can be generated from
    :param num_keys: the number of round keys needed
    :return:
    """
    key_list = []
    for i in range(0, num_keys):
        newkey = master_key[i*4:i*4+16]
        key_list.append(newkey)
    return key_list

def substitute_nibble(nibble_in: BitArray, encrypt: bool):
    """
    Substitute a set of four bits with another according the the s-box defined in Stinson
    :nibble_in: input nibble to be replaced
    :encrypt: set to True for encryption, False otherwise
    :return: substituted set of four bits
    """
    if nibble_in.length != 4:
        raise(ValueError('Input nibble is not four bits long.'))

    hex_str = str(nibble_in.hex)
    if(encrypt): return BitArray('0x' + str(sub_dict_encrypt[hex_str]))
    else: return BitArray('0x' + str(sub_dict_decrypt[hex_str]))


def substitute_two_bytes(bytes_in: BitArray, encrypt: bool):
    """
    Substitute a set of two bytes with another according the the s-box defined in Stinson
    :param bytes_in: input bytes to be replaced
    :param encrypt: set to True for encryption, False otherwise
    :return: substituted set of two bytes
    """
    if bytes_in.length != 16:
        raise(ValueError('Input must be sixteen bits long.'))

    output = BitArray()
    for i in range(0, 4):
        output.append(substitute_nibble(bytes_in[i*4:4*(i+1)], encrypt))
    return output

def permute_two_bytes(bytes_in: BitArray, encrypt: bool):
    """
    Permute the positions of two bytes
    :param bytes_in: Two bytes whos bits are to be scrambled
    :param encrypt: set to True for encryption, False otherwise
    :return: scrambled set of two bytes
    """
    output = BitArray('0x0000')
    if encrypt:
        for i in range(1,17):
            output[i-1] = bytes_in[perm_dict_encrypt[i]-1]
    else:
        for i in range(1,17):
            output[i-1] = bytes_in[perm_dict_decrypt[i]-1]
    return output

rounds = 2+1
# master key as given in Stinson
K = BitArray('0x8FA507')
keys = get_keys(K, rounds)
Y = BitArray('0xF5B2')
print('y   = 0x' + str(Y.hex))
K3 = keys[-1]
print('K^3 = ' + str(K3))
# key whitening
v2 = K3 ^ Y

# decryption round 1
print('v^2 = ' + str(v2))
u2 = substitute_two_bytes(v2, encrypt=False)
print('u^2 = ' + str(u2))
K2 = keys[-2]
print('K^2 = ' + str(K2))
w1 = K2 ^ u2

# decryption round 2
print('w^1 = ' + str(w1))
v1 = permute_two_bytes(w1, encrypt=False)
print('v^1 = ' + str(v1))
u1 = substitute_two_bytes(v1, encrypt=False)
print('u^1 = ' + str(u1))
K1 = keys[-3]
print('K^1 = ' + str(K1))
X = K1 ^ u1
print('X   = ' + str(X))