from bitstring import *

# Define dictionaries used for substititutions and pemutations
# substitution dictionary for encryption
sub_dict_encrypt = {
    '0': 8,
    '1': 4,
    '2': 2,
    '3': 1,
    '4': 12,
    '5': 6,
    '6': 3,
    '7': 13,
    '8': 10,
    '9': 5,
    'a': 14,
    'b': 7,
    'c': 15,
    'd': 11,
    'e': 9,
    'f': 0,
}

def substitute_nibble(nibble_in: BitArray):
    """
    Substitute a set of four bits with another according the the s-box defined in Stinson
    :nibble_in: input nibble to be replaced
    :encrypt: set to True for encryption, False otherwise
    :return: substituted set of four bits
    """
    if nibble_in.length != 4:
        raise(ValueError('Input nibble is not four bits long.'))
    hex_str = str(nibble_in.hex)
    return BitArray(uint=sub_dict_encrypt[hex_str], length = 4)
 
    
random_vars = [ [ None for i in range(8) ] for j in range(16) ]

for j in range(0, 16) :  
    input = BitArray(uint=j, length = 4)
    nibble = substitute_nibble(input)
    for i in range(0, 4):
        random_vars[j][i] = (input[i:i+1:1].int + 2) % 2 #for some reason it was making the 1's -1
    for k in range(0, 4):
        random_vars[j][k+4] = (nibble[k:k+1:1].int + 2) % 2 #for some reason it was making the 1's -1

linear_table = [ [ None for i in range(16) ] for j in range(16) ]

for a in range(0, 16):  
    for b in range(0, 16): 
        ax = BitArray(uint=a, length = 4)
        bx = BitArray(uint=b, length = 4)
        zeros_count = 0
        for d in range (0, 16): #each loop in d is a row in the random_vars table
            row_sum = 0
            for z in range (0, 4):
                row_sum += ax[z:z+1:1].int * random_vars[d][z]
            for c in range (0, 4):
                row_sum += bx[c:c+1:1].int * random_vars[d][c+4]
            zeros_count += ((row_sum + 1) % 2)
        
        linear_table[a][b] = zeros_count
        zeros_count = 0

print("Random Variables Table from new S-box: \n", random_vars)
print("Linear NL Table counting the number of zeroes that occur:\n", linear_table)
