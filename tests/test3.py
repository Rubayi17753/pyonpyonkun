from src.decomposer import decompose
from src.generate_subdict import generate_subdict1, generate_subdict2

def test3():
    ids = '⿰豸苗'
    ids2 = '丶{100}'
    ids3 = '⊖五一'
    ids4 = '車'
    ids5 = '王'
    subdict = generate_subdict2()
    print(subdict['土'])
    print('\n'.join(decompose(ids5, subdict, mode='all_decomp', keys_only=False)))

if __name__ == '__main__':
    test3()