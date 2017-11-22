from bitstring import *

# Define dictionaries used for substititutions and pemutations
# substitution dictionary for encryption
sub_dict_encrypt = {
    '0': '8',
    '1': '4',
    '2': '2',
    '3': '1',
    '4': 'c',
    '5': '6',
    '6': '3',
    '7': 'd',
    '8': 'a',
    '9': '5',
    'a': 'e',
    'b': '7',
    'c': 'f',
    'd': 'b',
    'e': '9',
    'f': '0',
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
    :return: a list of round keys
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

for i in range(1, 3):
    num_of_rounds = 4
    currInput = 0
    encrypt = True
    zeroCount = 0
    if i == 1:
        K = BitArray('0x93E026DE') #key 1
    else:
        K = BitArray('0xE5D7F82E') #key 2
        
    while currInput < 2**16:
        input = BitArray(uint=currInput, length=16)


        w_list = [BitArray()]*(num_of_rounds+1)
        u_list = [BitArray()]*(num_of_rounds+1)
        v_list = [BitArray()]*(num_of_rounds+1)
        key_array = get_keys(K, num_of_rounds+1)
        # pad the key_array to better fit with the algorithm given
        key_array = [None] + key_array

        w_list[0] = input
        for round_number in range(1, num_of_rounds):
            # perform a series of regular encryption rounds, including round key XOR, substitution, and permutation

            # XOR step
            u_list[round_number] = w_list[round_number-1] ^ key_array[round_number]
            # Substitution step
            v_list[round_number] = substitute_two_bytes(u_list[round_number], encrypt)
            # Permutation step
            w_list[round_number] = permute_two_bytes(v_list[round_number], encrypt)

        output = w_list[num_of_rounds-1] ^ key_array[num_of_rounds]
        currInput+=1
        output = output[0] ^ output[8] ^ input[15]

        if not output:
            zeroCount+=1

    print(zeroCount)
    print('The observed bias for key {0}  is: {1}'.format(i, (zeroCount / 2**16) - 0.5))