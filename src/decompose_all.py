import csv
import pandas as pd
from tqdm import tqdm
from functools import partial

from src.modules.fetch_prims import fetch_prims
from src.modules.commutative import generate_commutatives
from src.modules.decomposer import decompose
import src.modules.idc

import dirs

def decompose_all(df, subdict, omit_idc=1):

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

    def decompose1(ids, subdict):
        output, loop_status = decompose(ids, subdict)

        if loop_status:
            loop_text = '! INF LOOP !'
        else:
            loop_text = ''

        return output, loop_text

    dfdata_ids2 = [(chara, ids, *((chara, '') if chara in prims else decompose1(ids, subdict))) for (chara, ids) in tqdm(zip(charas, idss))]

    df3 = pd.DataFrame()
    df3[['chara', 'ids', 'ids2', 'loop']] = pd.DataFrame(dfdata_ids2)

    # Prepare dict_yaml
    def df_to_dict_yaml(df):
        df = df.explode('ids2').reset_index(drop=True)

        if omit_idc:
            for idc in tqdm(src.modules.idc.idc_all, desc='Deleting IDCs'):
                df['ids2'] = df['ids2'].str.replace(idc, '', regex=False)

        df_freq = pd.read_csv(dirs.freqlist_fp, sep='\t', header=None, names=['chara', 'freq', 'count'])
        df = pd.merge(df, df_freq, on='chara', how='left')
        df = df.sort_values(by=['freq',], ascending=[False,])
        df = df.drop_duplicates()

        return df[['chara', 'ids2']]
    
    df_dict_yaml = df_to_dict_yaml(df3)

    # df = df.explode('ids_expanded').reset_index(drop=True)
    # df = df[['unicode', 'chara', 'ids', 'ids_expanded', 'reg', 'ivi']]
    
    return df3, df_dict_yaml