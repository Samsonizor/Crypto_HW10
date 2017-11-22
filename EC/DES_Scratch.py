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

R = BitArray('0b 000110 110000 001011 101111 111111 000111 000001 110010 ')
print(R)
print(split_bitarray(R, 6))

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