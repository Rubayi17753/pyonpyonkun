from src.parser import parse_ids
from src.idc import idc_all, idc2, idc3

def ids2struct(s):

    output = dict()
    chars = parse_ids(s).split(',')
    chars_tuple = tuple(chars)      # tuples are immutable; note where they are used below

    def scan_ids(chars):

        for i, char in enumerate(chars_tuple):

            if char in idc_all:
                j = 3 if char in idc3 else 2
                sub_ids = chars[i: i+j]
                if all((True if x not in idc_all else False for x in sub_ids[1:])):

                    # i.e., if there is no other IDC in proximity to IDC.
                    # if there is none:
                    # create a sub-IDS, 
                    
                    chars[i: i+3] = (i,)  # within IDS, substitute sub-IDS with an index (equivalent to the IDC's index) 
                    output[i] = sub_ids         # add both index and sub-IDS into output

    while chars[0] != 0:
        scan_ids(chars)

    return output
        



