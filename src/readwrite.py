import pandas as pd
from tqdm import tqdm

import dirs
from src.generate_subdict import generate_custom_data
from src.generate_element_data import _generate_element_data
from src.generate_element_checklist import _generate_element_checklist
from src.element_data_to_secondary import _filter_secondary

def write_subdict():

    prims, prim_to_button = generate_custom_data()
    df_sub = write_element_data(output='two_lists', for_subdict=True, write_to='json')
    
    df_sub = df_sub[['element', 'sub_ids']]

    # Overwrite sub_ids set in custom_subs
    df_sub.loc[df_sub['element'].isin(prims), 'sub_ids'] = df_sub['element']

    subdict = pd.Series(df_sub['sub_ids'].values, index=df_sub['element']).to_dict()
    return subdict

def write_element_data(output='entries', read_from='x', write_to='json', write_dep=False, for_subdict=False):

    if read_from == 'x':
        read_from = write_to

    def process_data():
        if for_subdict:
            try:
                df = pd.read_json(dirs.ids_elements_fp_for_subdict, lines=True)
            except FileNotFoundError:
                print(f'{dirs.ids_elements_fp_for_subdict} not found. Generating element_data')
                df = _generate_element_data(output, write_to, write_dep)            

        elif read_from == 'json' and not write_dep:
            try:
                df = pd.read_json(dirs.ids_elements_fp_json, lines=True)
            except FileNotFoundError:
                print(f'{dirs.ids_elements_fp_json} not found. Generating element_data')
                df = _generate_element_data(output, write_to, write_dep)
        
        elif read_from == 'tsv' and not write_dep:
            try:
                df = pd.read_csv(dirs.ids_elements_fp_tsv, sep='\t')
            except FileNotFoundError:
                print(f'{dirs.ids_elements_fp_tsv} not found. Generating element_data')
                df = _generate_element_data(output, write_dep, write_to='tsv', sep='\t')

        else:
            df = _generate_element_data(output, write_to, write_dep)

        return df
    
    def write_data(df):
        
        df_written = df.copy()
        cols = df.columns.tolist()

        if not write_dep:
            if 'dep' in cols and 'dep2' in cols:
                del df_written['dep']
                del df_written['dep2']

        if write_to == 'json':
            print(f'Writing to {dirs.ids_elements_fp_json}')
            df_written.to_json(dirs.ids_elements_fp_json, orient='records', lines=True, force_ascii=False)

        elif write_to == 'tsv':
            print(f'Writing to {dirs.ids_elements_fp_tsv}')
            df_written.to_csv(dirs.ids_elements_fp_tsv, sep='\t', encoding='utf-8', index=False) 

    df = process_data()
    write_data(df)
    return df

def write_filter_secondary(refresh=False):

    df = None

    if not refresh:
        try:
            df = pd.read_csv(dirs.ids_elements_fp_tsv, sep='\t')
        except FileNotFoundError:
            df = write_element_data(output='entries', read_from='tsv', write_to='', write_dep=False)
    
    df = _filter_secondary(df)

    df.to_csv(dirs.secondaries_csv_fp, sep='\t', encoding='utf-8', index=False)
    with open(dirs.secondaries_json_fp, 'w', encoding='utf-8') as f:
        df.to_json(f, force_ascii='False')
    return df

def write_element_checklist():
    
    df = write_element_data(output='entries', read_from='tsv', write_to='', write_dep=False)
    df = _generate_element_checklist(df)
    df.to_csv(dirs.checklist_fp, sep='\t', encoding='utf-8', index=False)
    return df


