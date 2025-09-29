from src.modules.decomposer import decompose
from src.readwrite import write_subdict

def main():
    subdict = write_subdict()

    ids = None
    while ids != '':
        ids = input('Enter character (or press Enter to quit)\n')
        print('\n'.join(decompose(ids, subdict)))
    exit()

if __name__ == '__main__':
    main()