import time
import copy
import warnings
from src.modules.parser import parse_ids

def decompose(ids_main, subdict, mode='full_decomp', keys_only=1):

    output = 0
    outcome_dict = {ids_main: 2}
    # ids_prevs = set()

    # test_ids = '⿰丨⿼{50}一'
    # print(parse_ids(test_ids))
    # exit()
   
    def decompose_stage1(ids):
        idss = list()
        for char in parse_ids(ids):
            match = subdict.get(char, '')   # subdict: chara (str) -> subs (list)
            if match:

                ids2 = str(ids)
                for sub in parse_ids(match):
                    ids2 = ids.replace(char, sub)

                idss.append(ids2) if idss != ids else ...

        return set(idss)          # [s for s in idss if s != ids]

    def decompose_stage2():
        for ids in outcome_dict.copy():
            # print(f' {ids} > {decompose_stage1(ids)}')

            for ids_new in decompose_stage1(ids):
                if ids_new == ids:
                    outcome_dict[ids_new] = 0
                else:
                    outcome_dict[ids], outcome_dict[ids_new] = 1, 2

    i = 0
    while 2 in outcome_dict.values():
        decompose_stage2()
        
        i += 1
        if i >= 30:
            # warnings.warn(f'WARNING: infinite loop suspected while decomposing {ids_main}')
            return ['! INF LOOP !',]

        # print(outcome_dict)

    if mode == 'full_decomp':
        output = {mykey : myvalue for mykey, myvalue in outcome_dict.items() if myvalue == 0}
    elif mode == 'all_decomp':
        output = outcome_dict
    elif mode == 'separate':
        output = (
            {mykey : myvalue for mykey, myvalue in outcome_dict.items() if myvalue == 1},
            {mykey : myvalue for mykey, myvalue in outcome_dict.items() if myvalue == 0},
            )
    
    if keys_only:
        output = list(output.keys())
    
    return output
        
