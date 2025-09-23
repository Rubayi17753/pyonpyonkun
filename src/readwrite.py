import os
import pandas as pd
from tqdm import tqdm

import dirs
from src.generate_prim_data import generate_prim_data
from src.generate_element_data import _generate_element_data
from src.generate_element_checklist import _generate_element_checklist
from src.element_data_to_secondary import _filter_secondary
from src.modules.fetch_config import fetch_prims

def write_subdict():

    prims = fetch_prims(include_compounds=False)
    df_sub = write_element_data(fp=dirs.ids_elements_fp_for_subdict, 
                                output='two_lists')
    
    df_sub = df_sub[['element', 'sub_ids']]

    # Overwrite sub_ids set in custom_subs
    df_sub.loc[df_sub['element'].isin(prims), 'sub_ids'] = df_sub['element']

    subdict = pd.Series(df_sub['sub_ids'].values, index=df_sub['element']).to_dict()
    return subdict

def write_element_data(fp='',
                       read_fp='',
                       write_fp='',
                       output='entries',  
                       write_dep=False):

    read_fp = fp if read_fp == '' else ''
    write_fp = fp if write_fp == '' else ''
    rformat = os.path.splitext(read_fp)[1] if read_fp else ''
    wformat = os.path.splitext(write_fp)[1] if write_fp else ''

    def process_data():

        try:
            if rformat == '.tsv':
                df = pd.read_csv(read_fp, encoding='utf-8', sep='\t')
            elif rformat == '.json':
                df = pd.read_json(read_fp, lines=True)
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            print(f'{read_fp} not found. Generating element_data')
            df = _generate_element_data(output)

        return df
    
    def write_data(df):
        
        df_written = df.copy()
        cols = df.columns.tolist()

        if not write_dep:
            if 'dep' in cols and 'dep2' in cols:
                del df_written['dep']
                del df_written['dep2']
        else:
            pass

        if write_fp:
            print(f'Writing to {write_fp}')
            if wformat == '.tsv':
                df_written.to_csv(write_fp, sep='\t', encoding='utf-8', index=False)
            elif wformat == '.json':
                df_written.to_json(write_fp, orient='records', lines=True, force_ascii=False)
        else:
            pass
 
    df = process_data()
    write_data(df)
    return df

def write_filter_secondary():

    df = write_element_data(fp=dirs.ids_elements_fp_tsv,
                output='entries',  
                write_dep=False)
    df = _filter_secondary(df)

    df.to_csv(dirs.secondaries_csv_fp, sep='\t', encoding='utf-8', index=False)
    with open(dirs.secondaries_json_fp, 'w', encoding='utf-8') as f:
        df.to_json(f, force_ascii='False')
    return df

def write_element_checklist():
    
    df = write_element_data(fp=dirs.ids_elements_fp_tsv,
                       output='entries',  
                       write_dep=False)
    df = _generate_element_checklist(df)
    df.to_csv(dirs.checklist_fp, sep='\t', encoding='utf-8', index=False)
    return df


