from bitstring import BitArray
import numpy as np
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
    perform permuation on input data 
    :param data_in: input data
    :return: 
    """
    shape   = (len(permutation_mat), len(permutation_mat[0]))
    output  = [[False]*shape[1] for i in range(0,shape[0])]
    for row,col in iter.product(range(0, shape[0]), range(0, shape[1])):
        index = permutation_mat[row][col]
        output[row][col] = data_in[index-1]
    return output

def split_bitarray(tosplit: BitArray, n: int):
    """
    split a BitArray into an array of BitArrays, each of length n
    :param tosplit: BitArray to be split, length MUST NOT be prime
    :param n: length of sub-arrays to be made, MUST be a factor of len(tosplit)
    :return: an array of BitArrays of length len(tosplit)/n
    """
    if not len(tosplit) % n == 0:
        raise ValueError('n does not divide the length of tosplit')
    output = []
    for i in range(0, int(len(tosplit)/n)):
        ba_temp = tosplit[i*n:(i+1)*n]
        output.append(ba_temp)
    return output

# R = BitArray('0b 000110 110000 001011 101111 111111 000111 000001 110010 ')
# print(R)
# print(split_bitarray(R, 6))

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

def do_f(R: BitArray, K: BitArray, debug = False):
    """
    'f' function used in the DES encryption process
    :param R: a 32-bit block of data 
    :param K: a 48-bit block of data (typically a subkey)
    :param debug: set to true if debugging print statements are needed
    :return: the 32-bit output of f
    """
    # initial checks
    if(len(R) != 32):
        raise ValueError('R does not have a length of 32')
    if(len(K) != 48):
        raise ValueError('K does not have a length of 48')
    # Expand R
    R_expanded = BitArray(flatten_list(do_permutation(R, vals.E)))
    if debug: print('E(R): %s' % R_expanded.bin)
    # XOR E(R) with subkey
    RK_Sum = R_expanded ^ K
    if debug: print('E(R) + K: %s' % RK_Sum.bin)
    # split the sum in to portions of length 6 and perform S-boxes on each
    RK_Sum_Split =  split_bitarray(RK_Sum, 6)
    for i in range(0,len(RK_Sum_Split)):
        box = vals.sbox_array[i]
        sum_element = RK_Sum_Split[i][:]
        col = sum_element[1:5].uint
        del sum_element[1:5]
        row = sum_element.uint
        box_result = box[row][col]
        RK_Sum_Split[i] = BitArray(uint=box_result, length=4)
    boxed_sum = BitArray()
    for sum_element in RK_Sum_Split:
        boxed_sum.append(sum_element)
    if debug: print('S-Box result: %s' % boxed_sum.bin)
    # perform the final permutatin
    output = BitArray(flatten_list(do_permutation(boxed_sum, vals.P)))
    if debug: print('output of f: %s' % output.bin)
    return output

# The below can be used to validate the functionality of initial_permutation as described in
# http://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm
# R = BitArray('0b 1111 0000 1010 1010 1111 0000 1010 1010')
# K = BitArray('0b 000110 110000 001011 101111 111111 000111 000001 110010 ')
# do_f(R, K, debug=True)

def DES_encrypt(plaintext: BitArray, key_seed: BitArray, debug=False):
    """
    DES-Encrypt plaintext using the given key
    :param plaintext: Plaintext to be encrypted - MUST be 64 bits long
    :param key_seed: Key used to encrypt - MUST be 64 bits long
    :param debug: set to true if debugging print statements are needed
    :return: encrypted data of length 64
    """
    # initial checks
    if (len(plaintext) != 64):
        raise ValueError('plaintext does not have a length of 32')
    if (len(key_seed) != 64):
        raise ValueError('key seed does not have a length of 64')
    # Initalize left and right lists
    L = [BitArray() for i in range(0, 17)]
    R = [BitArray() for i in range(0, 17)]
    keylist = get_subkeys(key_seed, debug=False)
    if debug:
        print('\nSubkey values:')
        for i in range(0, len(keylist)):
            print('K_%s = %s' % (i, keylist[i].bin))
    IP_plaintext = [BitArray(element) for element in do_permutation(plaintext, vals.ip)]
    temp_l = BitArray(flatten_list(IP_plaintext[:4]))
    temp_r = BitArray(flatten_list(IP_plaintext[4:]))
    [R[0], L[0]] = [temp_r, temp_l]
    for i in range(1,17):
        L[i] = R[i-1]
        R[i] = L[i-1] ^ do_f(R[i-1], keylist[i])
    if debug:
        print('\nL values:')
        for i in range(0, len(L)):
            print('L_%s = %s' % (i, L[i].bin))
        print('\nR values:')
        for i in range(0, len(R)):
            print('R_%s = %s' % (i, R[i].bin))
    # R_fin = np.array(R[16])
    # L_fin = np.array(L[16])
    output_pre_permutation = np.concatenate((split_bitarray(R[16], 4), split_bitarray(L[16], 4)), axis=0)
    output = do_permutation(BitArray(flatten_list(output_pre_permutation.tolist())), vals.ip_inv)
    if debug:
        print('Ciphertext before inverse permutation: ')
        for element in output_pre_permutation:
            print(BitArray(element).bin)
    return BitArray(flatten_list(output))

# The below can be used to validate the functionality of DES_encrypt() as described in
# http://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm
# x   = BitArray('0b 0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111')
# K   = BitArray('0b 00010011 00110100 01010111 01111001 10011011 10111100 11011111 11110001')
# y = DES_encrypt(x, K, debug=True)
# print('\nCiphertext:' + str(y.hex))