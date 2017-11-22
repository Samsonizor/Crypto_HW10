from bitstring import BitArray
import EC.DES_VALS as vals
import itertools as iter

shape = (3,4)
output  = [[False]*shape[0] for i in range(0,shape[1])]

i = 1+1