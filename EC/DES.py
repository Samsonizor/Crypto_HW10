from bitstring import BitArray
import EC.DES_VALS as vals
import itertools as iter

def flatten_list(list: list):
    """
    Takes a list of lists and 'flattens' it to a list
    :param list: list to be flattened
    :return: flattened list
    """
    iter_list = iter.chain.from_iterable(list)
    lst = []
    for item in iter_list:
        lst.append(item)
    return lst

def do_permutation(data_in: BitArray, permutation_mat: list):
    """
    perform initial permuation on input data (usually the plaintext)
    :param data_in: input data
    :return: 
    """
    shape   = (len(permutation_mat), len(permutation_mat[0]))
    output  = [[False]*shape[1] for i in range(0,shape[0])]
    for row,col in iter.product(range(0, shape[0]), range(0, shape[1])):
        index = permutation_mat[row][col]
        output[row][col] = data_in[index-1]
    return output

# The below can be used to validate the functionality of initial_permutation as described in
# http://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm
# M   = BitArray('0b 0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111')
# for item in do_permutation(M, vals.ip_mat):
#     print(BitArray(item).bin)

def get_subkeys(seed: BitArray, debug = False):
    """
    Get the set of 16 48-bit subkeys needed for the DES algorithm
     seed determines the value of these keys
    :param seed: seed key
    :param debug: set to true if debugging print statements are needed
    :return: an array of the 16 subkeys
    """
    # initialize C and D arrays to all zeros
    C = [[False]*28 for i in range(0,17)]
    D = [[False]*28 for i in range(0,17)]
    # first, get initial values for C and D
    key_permuted = do_permutation(seed, vals.pc_1)
    if debug:
        print('Permuted key value: %s'
              % str(key_permuted))
    C[0] = BitArray(flatten_list(key_permuted[0:4]))
    D[0] = BitArray(flatten_list(key_permuted[4:]))
    shift_amnts = vals.keygen_shift_table
    for i in range(1,17):
        C_prev = BitArray(C[i-1])
        C_prev.rol(shift_amnts[i - 1])
        C[i] = C_prev
        D_prev = BitArray(D[i - 1])
        D_prev.rol(shift_amnts[i - 1])
        D[i] = D_prev
    # print values of C and D if debug flag is set
    if debug:
        print('\nC values:')
        for i in range(0, len(C)):
            print('C_%s = %s' % (i, C[i].bin))
        print('\nD values:')
        for i in range(0, len(D)):
            print('D_%s = %s' % (i, D[i].bin))
    # create the subkeys based on the C and D values
    K = []
    for i in range(0, 17):
        k_temp = BitArray(C[i]+D[i])
        K.append(BitArray(flatten_list(do_permutation(k_temp, vals.pc_2))))
    if debug:
        print('\nSubkey values:')
        for i in range(0, len(K)):
            print('K_%s = %s' % (i, K[i].bin))
    return K

# The below can be used to validate the functionality of get_subkeys as described in
# http://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm
# K = BitArray('0b 00010011 00110100 01010111 01111001 10011011 10111100 11011111 11110001')
# get_subkeys(K, debug=True)

# Initialize given values
x   = BitArray('0b 00100101 01100111 11001101 10110011 11111101 11001110 01111110 00101010')
K   = BitArray('0b 11100101 01100111 11001101 10110011 11111101 11001110 01111111 00101010')