import csv
import pandas as pd
from tqdm import tqdm
from functools import partial

from src.modules.fetch_prims import fetch_prims
from src.modules.idsi import lint_ids

import dirs

def main():

    with open(dirs.ids_processed_fp, 'r', encoding='utf-8') as f:
        df = pd.read_csv(f, sep='\t', header=None, names=['unicode', 'chara', 'ids', 'reg', 'ivi'])

    prims, prim_to_cyp, lat_to_prim = fetch_prims()

    df['ids_neg'] = df['ids'].apply(lambda x: '㇯' in x)
    df = df[~df['ids_neg']]
    del df['ids_neg']

    idss = df['ids'].to_list()
    for i, ids in enumerate(idss):
        if lint_ids(ids):
            print(f'Malformed IDS at line {i}')
            