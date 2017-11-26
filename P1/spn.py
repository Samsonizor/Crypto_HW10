from bitstring import *

# Change s_box dictionary to alter s-box behaviour
# Change permutation_map to alter the permutation mapping
# Currently, s_box and permutation_map reflect Stinson 3.2
# Change the input, key, and rounds (near end of this file) to alter the spn input, spn key, and the number of spn rounds respectively
# Change verbosity to dictate whether or not spn output is suppressed

# Define dictionaries used for substititutions and pemutations
# substitution dictionary for encryption
s_box = {
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
sub_dict_decrypt = {v: k for k, v in s_box.items()}

# permutation dictionary for encryption
permutation_map = {
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
perm_dict_decrypt = {v: k for k, v in permutation_map.items()}

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
    if(encrypt): return BitArray('0x' + str(s_box[hex_str]))
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
            output[i-1] = bytes_in[permutation_map[i] - 1]
    else:
        for i in range(1,17):
            output[i-1] = bytes_in[perm_dict_decrypt[i]-1]
    return output


def spn_process(input: BitArray, key :BitArray, num_rounds=2, encrypt=True, verbose=False):
    w_list = [BitArray()] * (num_rounds + 1)
    u_list = [BitArray()] * (num_rounds + 1)
    v_list = [BitArray()] * (num_rounds + 1)
    key_array = get_keys(key, num_rounds + 1)
    # pad the key_array to better fit with the algorithm given
    key_array = [None] + key_array
    if encrypt:
        w_list[0] = input
        for round_number in range(1, num_rounds):
            # perform a series of regular encryption rounds, including round key XOR, substitution, and permutation

            # XOR step
            u_list[round_number] = w_list[round_number - 1] ^ key_array[round_number]
            # Substitution step
            v_list[round_number] = substitute_two_bytes(u_list[round_number], encrypt)
            # Permutation step
            w_list[round_number] = permute_two_bytes(v_list[round_number], encrypt)

        # final round which excludes permutation
        u_list[num_rounds] = w_list[num_rounds - 1] ^ key_array[num_rounds]
        v_list[num_rounds] = substitute_two_bytes(u_list[num_rounds], encrypt)
        output = v_list[num_rounds] ^ key_array[num_rounds + 1]
    else:  # decryption
        w_list[num_rounds] = input
        v_list[num_rounds] = w_list[num_rounds] ^ key_array[num_rounds + 1]
        u_list[num_rounds] = substitute_two_bytes(v_list[num_rounds], encrypt)
        w_list[num_rounds - 1] = u_list[num_rounds] ^ key_array[num_rounds]
        for round_number in range(num_rounds - 1, 0, -1):
            # Permutation step
            v_list[round_number] = permute_two_bytes(w_list[round_number], encrypt)
            # Substitution step
            u_list[round_number] = substitute_two_bytes(v_list[round_number], encrypt)
            # XOR step
            w_list[round_number - 1] = u_list[round_number] ^ key_array[round_number]

        output = w_list[0]
    if verbose:
        print("w_list: {0}, ".format(w_list))
        print("u_list: {0}, ".format(u_list))
        print("v_list: {0}, ".format(v_list))
        print("key array: {0}".format(key_array))
    return output

input = BitArray('0xF5B2')  # works for B33C -> F5B2
key = BitArray('0x8FA507')
rounds = 2
verbosity = True

output = spn_process(input, key, encrypt=False, verbose=verbosity)
print('Output: %s' % output)