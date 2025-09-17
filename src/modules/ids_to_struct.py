from src.modules.parser import parse_ids
from src.modules.idc import idc2, idc3

def ids2struct(s):

    chars = parse_ids(s).split(',')
    output = list()
    curr = list()


    for char in chars:

        if char in idc2:
            output.append([char, ])
            curr = ...
        else:
            ...