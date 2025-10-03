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

    charas = df['chara'].to_list()
    idss = df['ids'].to_list()
    dfdata_ids_comm = [(chara, generate_commutatives(ids)) for (chara, ids) in tqdm(zip(charas, idss))]
    # df['ids_comm'] = pd.Series(ids_comm)

    df2 = pd.DataFrame()
    df2[['chara', 'ids']] = pd.DataFrame(dfdata_ids_comm)
    # df['ids'] = df['ids'].apply(generate_commutatives)
    df = df.explode('ids').reset_index(drop=True)
    df['ids'] = df['ids'].fillna('!NaN!')

    # serie = df['ids_comm'][df['ids_comm'].apply(lambda x: not isinstance(x, str))]
    # print(serie)

    charas = df['chara'].to_list()
    idss = df['ids'].to_list()
    dfdata_ids2 = [(chara, ids, [ids,] if ids in prims else decompose(ids, subdict)) for (chara, ids) in tqdm(zip(charas, idss))]

    df3 = pd.DataFrame()
    df3[['chara', 'ids', 'ids2']] = pd.DataFrame(dfdata_ids2)
    # df = df.explode('ids_expanded').reset_index(drop=True)
    # df = df[['unicode', 'chara', 'ids', 'ids_expanded', 'reg', 'ivi']]
    
    return df3