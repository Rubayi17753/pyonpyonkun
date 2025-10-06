from src.modules.decomposer import decompose
from src.readwrite import write_subdict

def main():
    subdict = write_subdict()

    ids = None
    while ids != '':
        ids = input('Enter IDS (or press Enter to quit)\n')
        output, loop_status = decompose(ids, subdict, debug_mode=1)
        print('\n'.join(output))
    exit()

if __name__ == '__main__':
    main()