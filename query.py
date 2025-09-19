from src.modules.decomposer import decompose
from src.generate_subdict import generate_subdict

def main():
    subdict = generate_subdict()
    ids = None
    while ids != '':
        ids = input('Enter character (or press Enter to quit)\n')
        print('\n'.join(decompose(ids, subdict)))
    exit()

if __name__ == '__main__':
    main()