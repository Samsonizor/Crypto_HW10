from bitstring import BitArray
import EC.DES_VALS as vals
import numpy as np
import itertools as iter

def do_permutation(data_in: BitArray, permutation_mat: np.matrix):
    """
    perform initial permuation on input data (usually the plaintext)
    :param data_in: input data
    :return: 
    """
    shape   = permutation_mat.shape
    output  = np.zeros(shape)
    for row,col in iter.product(range(0, shape[0]), range(0, shape[1])):
        index = permutation_mat[row,col]
        output[row,col] = data_in[index-1]
    return output

# The below can be used to validate the functionality of initial_permutation as described in
# http://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm
# M   = BitArray('0b 0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111')
# print(do_permutation(M, vals.ip_mat))

def get_subkeys(seed: BitArray, debug = False):
    """
    Get the set of 16 48-bit subkeys needed for the DES algorithm
     seed determines the value of these keys
    :param seed: seed key
    :param debug: set to true if debugging print statements are needed
    :return: an array of the 16 subkeys
    """
    key_permuted = do_permutation(seed, vals.pc_1)
    C = key_permuted[0:4,:]
    D = key_permuted[4:,:]
    if debug:
        print('C value: %s \n\n D value: %s \n\n Permuted key value: %s' % (str(C), str(D), str(key_permuted)))

# The below can be used to validate the functionality of get_subkeys as described in
# http://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm
# K = BitArray('0b 00010011 00110100 01010111 01111001 10011011 10111100 11011111 11110001')
# get_subkeys(K, debug=True)

# Initialize given values
x   = BitArray('0b 00100101 01100111 11001101 10110011 11111101 11001110 01111110 00101010')
K   = BitArray('0b 11100101 01100111 11001101 10110011 11111101 11001110 01111111 00101010')