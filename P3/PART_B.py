from numpy import polydiv

def sbox_AES(input):
    """
    perform the AES s-box on the input
    :param input: s-box input
    :return: result of the s-box
    """

# AES Values
AES_S_BOX = [[1, 0, 0, 0, 1, 1, 1, 1],
             [1, 1, 0, 0, 0, 1, 1, 1],
             [1, 1, 1, 0, 0, 0, 1, 1],
             [1, 1, 1, 1, 0, 0, 0, 1],
             [1, 1, 1, 1, 1, 0, 0, 0],
             [0, 1, 1, 1, 1, 1, 0, 0],
             [0, 0, 1, 1, 1, 1, 1, 0],
             [0, 0, 0, 1, 1, 1, 1, 1]]

REDUCING_POLY = [1,0,0,0,1,1,0,1,1]

# Values given in problem 3b
Z = [[None],
     [0,0,0,0,0,0,0,0],
     [0,0,0,0,0,0,0,1],
     [0,0,0,0,0,0,1,0],
     [0,0,0,0,0,0,1,1]]

