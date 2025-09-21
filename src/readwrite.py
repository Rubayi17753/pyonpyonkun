import pandas as pd
from tqdm import tqdm

import dirs
from src.generate_subdict import generate_custom_data
from src.generate_element_data import _generate_element_data
from src.generate_element_resume import _generate_element_summary

def write_subdict():

    prims, prim_to_button = generate_custom_data()
    df_sub = _generate_element_data(output='two_lists')
    
    df_sub = df_sub[['element', 'sub_ids']]

    # Overwrite sub_ids set in custom_subs
    df_sub.loc[df_sub['element'].isin(prims), 'sub_ids'] = df_sub['element']

    subdict = pd.Series(df_sub['sub_ids'].values, index=df_sub['element']).to_dict()
    return subdict

def write_element_data(output='entries', read_from='x', write_to='json', write_dep=False):

    if read_from == 'x':
        read_from = write_to

    def process_data():
        if read_from == 'json':
            try:
                df = pd.read_json(dirs.ids_elements_fp_json, lines=True)
            except FileNotFoundError:
                print(f'{dirs.ids_elements_fp_json} not found. Generating element_data')
                df = _generate_element_data(output, write_to, write_dep)
        
        elif read_from == 'tsv':
            try:
                df = pd.read_csv(dirs.ids_elements_fp_tsv, lines=True)
            except FileNotFoundError:
                print(f'{dirs.ids_elements_fp_tsv} not found. Generating element_data')
                df = _generate_element_data(output, write_dep, write_to='tsv')

        else:
            df = _generate_element_data(output, write_to, write_dep)

        return df
    
    def write_data(df):
        
        df_written = df.copy()

        if not write_dep:
            del df_written['dep']
            del df_written['dep2']

        if write_to == 'json':
            print(f'Writing to {dirs.ids_elements_fp_json}')
            df_written.to_json(dirs.ids_elements_fp_json, orient='records', lines=True, force_ascii=False)

        elif write_to == 'tsv':
            print(f'Writing to {dirs.ids_elements_fp_tsv}')
            df_written.to_tsv(dirs.ids_elements_fp_tsv, sep='\t', encoding='utf-8', index=False) 

    df = process_data()
    write_data(df)
    return df

def write_element_summary():
    
	fp = write_element_data(output='entries', read_from='tsv', write_to='', write_dep=False)
	fp = _generate_element_summary(fp)
	print(fp)
	exit()
