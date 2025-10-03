"""
IDSI = Ideographical Description Sequence *Index*:
    a flat dictionary that shows the immediate components of each IDC (dotted boxes in IDS)
    mapping as follows
        index (position of IDC)
        components, consisting of the IDC itself (always element 0), and 
        two or three other elements (can be either:
            character
            unary operator + char                       # for IDSI purposes not considered as IDC
            unencoded component:    {n} where n > 1     # see babelstone/IDS.txt
            index pointing to another IDC and its components
                (hereinafter known as sub-IDS)
"""

import copy

from src.modules.parser import parse_ids
from src.modules.idc import idc_all, idc2, idc3, idc_to_len

def ids_to_idsi(s: str) -> dict:

    idsi = dict()
    chars = parse_ids(s)

    def scan_ids(chars):

        # tuple() is neccesitated by the fact that lists cannot be iterated and modified at the same time
        for i, char in enumerate(tuple(chars)):
            if char in idc_all:

                j = 4 if char in idc3 else 3
                sub_ids = chars[i: i+j]
                # print(f'>> {i}, {i+j} : {sub_ids}')

                if sub_ids and all((True if x not in idc_all else False for x in sub_ids[1:])):

                    # i.e., if there is no other IDC in proximity to IDC.
                    # if there is none:
                    # create a sub-IDS, 
                    
                    chars[i: i+j] = (i,)  # within IDS, substitute sub-IDS with an index (equivalent to the IDC's index) 
                    idsi[i] = copy.deepcopy(sub_ids)         # add both index and sub-IDS into output

    if all([char not in idc_all for char in chars]):
        pass
    else:               
        while chars[0] != 0:
            scan_ids(chars)

    return idsi

def idsi_to_ids(idsi: dict, starting_index = 0, return_type=str) -> str:

    # basic idea: code substitute integers for sub-IDS until no integers left in IDS

    ids = idsi.get(starting_index, '')

    while not all((not isinstance(x, int) for x in ids)):
        for i, dep in enumerate(ids.copy()):
            if isinstance(dep, int):
                ids[i: i+1] = idsi.get(dep, '')
                
    if return_type == str:
        return ''.join(ids)
    elif return_type == list:
        return ids
    else:
        return return_type(ids)
    
def lint_idsi(idsi: dict):

    '''
        if not lint, corresponds to valid IDS
        otherwise returns a list of index indicating the positions of: 
        - characters misidentified as IDS
        - IDCs with irregular number of components
    '''
    lint1, lint2 = tuple(), tuple()

    lint1 = tuple((index for index, sub_ids in zip(idsi.keys(), idsi.values()) if sub_ids[0] not in idc_all))

    if not lint1:
        lint2 = tuple((index for index, sub_ids in zip(idsi.keys(), idsi.values()) if idc_to_len[sub_ids[0]] != len(sub_ids) - 1))

    return lint1, lint2

def lint_ids(s):

    idsi = ids_to_idsi(s)

    lint1, lint2 = lint_idsi(idsi)
    if lint1:
        lint_msg = f'Invalid IDS {s} \nIDSI: {idsi} \nWrongly identified IDCs in position(s) {", ".join(str(lint1))}'
    elif lint2:
        lint_msg = f'Invalid IDS {s} \nIDSI: {idsi} \nIDCs with irregular number of components in position(s) {", ".join(str(lint2))}'
    else:
        return 0
    
    return lint_msg








