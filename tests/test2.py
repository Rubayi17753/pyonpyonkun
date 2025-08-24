from src.parser import parse_ids

def test2():
    brack1 = parse_ids('⿻⿻⿰𠄌丶人𠄌')
    print(''.join(brack1))

if __name__ == '__main__':
    test2()