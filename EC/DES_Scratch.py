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

M   = BitArray('0b 0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111')
print(BitArray(do_permutation(M, vals.ip_mat).flatten()))