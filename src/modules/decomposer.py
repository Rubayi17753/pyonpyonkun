from src.modules.parser import parse_ids

def decompose_stage1(s, subdict):
    for char in parse_ids(s):
        if char in subdict:
            for sub in subdict.get(char, [char]):
                s = s.replace(char, sub)
    return s

def decompose(ids_main, subdict, mode='full_decomp', keys_only=1):

    output = 0
    ids_prevs = set()
    outcome_dict = {ids_main: 2}

    def decompose_stage2():
        for ids in outcome_dict.copy():

            ids_new = decompose_stage1(ids, subdict)

            if ids_new == ids:
                outcome_dict[ids_new] = 0
            else:
                # ids_prevs.add(ids_new)
                outcome_dict[ids], outcome_dict[ids_new] = 1, 2

    while 2 in outcome_dict.values():
        decompose_stage2()

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
        


        
