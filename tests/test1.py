from src.commutative import clonemirror

def test1():
    brack1 = clonemirror('(⿻,(⿻,(⿰,𠄌,丶),人),𠄌)')
    print('\n'.join(brack1))

if __name__ == '__main__':
    test1()