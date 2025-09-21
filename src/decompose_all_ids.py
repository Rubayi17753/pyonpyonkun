import tsv
from tqdm import tqdm
from src.modules.decomposer import decompose
from src.generate_subdict import generate_subdict

def main():

    data_fp = 'data/ids_elements.tsv'

    with open(data_fp, 'r', encoding='utf-8') as tsvfile:
        myreader = tsv.reader(tsvfile, delimiter='\t')
        rows = list(myreader)
        
        subdict = generate_subdict()
        output = list()
        for row in tqdm(rows):
            # ids: unicode, char, ids, *_
            # ids_elements: char, sub, key, ids, *_
            char, sub, key, ids = row

            if '⊖' in ids:
                output.append((char, ids, ''))
            else:
                for decomp in decompose(char, subdict):
                    output.append((char, ids, decomp))

    with open(data_fp.replace('data/', 'data/decomposed/'), 'w', encoding='utf-8', newline='') as tsvout:
        spamwriter = tsv.writer(tsvout, delimiter='\t')
        spamwriter.writerows(output)
