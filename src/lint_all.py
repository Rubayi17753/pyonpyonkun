import csv
import pandas as pd
from tqdm import tqdm
from functools import partial

from src.modules.fetch_prims import fetch_prims
from src.modules.idsi import lint_ids

import dirs

def main():

    # from src.modules.idc import idc_to_len
    # print(idc_to_len)
    # exit()

    with open(dirs.ids_processed_fp, 'r', encoding='utf-8') as f:
        df = pd.read_csv(f, sep='\t', header=None, names=['unicode', 'chara', 'ids', 'reg', 'ivi'])

    # prims, prim_to_cyp, lat_to_prim = fetch_prims()

    out_msg = list()

    df['ids_neg'] = df['ids'].apply(lambda x: '㇯' in x)
    df = df[~df['ids_neg']]
    del df['ids_neg']

    idss = df['ids'].to_list()
    for i, ids in enumerate(idss):
        lint_msg = lint_ids(ids)
        if lint_msg:
            out_msg.append(f'\n\nMalformed IDS at line {i}')
            out_msg.append(lint_msg)

    with open(dirs.ids_lint_report_fp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_msg))
            