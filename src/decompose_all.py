import csv
import pandas as pd
from tqdm import tqdm
from functools import partial

from src.modules.fetch_prims import fetch_prims
from src.modules.commutative import generate_commutatives
from src.modules.decomposer import decompose

def decompose_all(df, subdict):

    prims, prim_to_cyp, lat_to_prim = fetch_prims()

    df['ids_neg'] = df['ids'].apply(lambda x: '㇯' in x)
    df = df[~df['ids_neg']]
    del df['ids_neg']

    idss = df['ids'].to_list()
    ids_comm = [generate_commutatives(x) for x in tqdm(idss)]
    df['ids_comm'] = pd.Series(ids_comm)
    # df['ids_comm'] = df['ids'].apply(generate_commutatives)
    df = df.explode('ids_comm').reset_index(drop=True)

    charas = df['chara'].to_list()
    idss = df['ids_comm'].to_list()
    ids2 = [x if x in prims else decompose(x, subdict) for x in tqdm(idss)]

    df2 = pd.DataFrame({'chara': charas, 'ids': idss, 'ids2': ids2})
    # df = df.explode('ids_expanded').reset_index(drop=True)
    # df = df[['unicode', 'chara', 'ids', 'ids_expanded', 'reg', 'ivi']]
    
    return df2