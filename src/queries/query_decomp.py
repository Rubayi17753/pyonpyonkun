from src.modules.decomposer import decompose
from src.modules.commutative import generate_commutatives
from src.readwrite import write_subdict

def main(debug_mode=0):
    subdict = write_subdict()

    ids = None
    while ids != '':
        ids = input('Enter IDS (or press Enter to quit)\n')

        output_all = list()
        for ids2 in generate_commutatives(ids):
            output, loop_status = decompose(ids2, subdict, debug_mode=debug_mode)
            output_all.extend(output)

        print('\n'.join(output_all))

if __name__ == '__main__':
    main()