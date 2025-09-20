import pandas as pd
from tqdm import tqdm

import dirs
import src.generate_element_data_utils as utils

def _generate_element_data(output='entries', write_to='json', include_dep=False):

    funcs = ['_preprocess',
    '_insert_char_count',
    '_freqdict',
    '_insert_dep',
    '_insert_freq1',
    '_insert_elm_type',
    '_insert_dep2',
    '_insert_freq2',
    '_insert_freq',
    '_insert_stroke',
    '_insert_sub_ids_regions',
    '_split_sub_ids_regions',
    '_drop_dupl_and_sort',
    '_arrange_cols_',]

    df_ids = utils.read_ids()
    df = df_ids.copy()

    for func in tqdm(funcs):
        if func == '_freqdict':
            freqdict = getattr(utils, func)(df)
        elif func in {'_insert_freq1', '_insert_freq2',}:
            df = getattr(utils, func)(df, freqdict)
        elif func in {'_insert_sub_ids_regions', '_split_sub_ids_regions', '_arrange_cols_'}:
            df = getattr(utils, func)(df, output)                    
        else:
            df = getattr(utils, func)(df)

    return df

def generate_element_data(output='entries', read_from='x', write_to='json', include_dep=False):

    if read_from == 'x':
        read_from = write_to

    def process_data():
        if read_from == 'json':
            try:
                df = pd.read_json(dirs.ids_elements_fp_json, lines=True)
            except FileNotFoundError:
                print(f'{dirs.ids_elements_fp_json} not found. Generating element_data')
                df = _generate_element_data(output, write_to, include_dep)
        
        elif read_from == 'csv':
            try:
                df = pd.read_json(dirs.ids_elements_fp_csv, lines=True)
            except FileNotFoundError:
                print(f'{dirs.ids_elements_fp_csv} not found. Generating element_data')
                df = _generate_element_data(output, include_dep, write_to='csv')

        else:
            df = _generate_element_data(output, write_to, include_dep)

        return df
    
    def write_data(df):

        if not include_dep:
            del df['dep']

        if write_to == 'json':
            print(f'Writing to {dirs.ids_elements_fp_json}')
            df.to_json(dirs.ids_elements_fp_json, orient='records', lines=True, force_ascii=False)

        elif write_to == 'csv':
            print(f'Writing to {dirs.ids_elements_fp_csv}')
            df.to_csv(dirs.ids_elements_fp_csv, sep='\t', encoding='utf-8', index=False) 

    df = process_data()
    write_data(df)
    return df

