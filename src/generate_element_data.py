import pandas as pd
from tqdm import tqdm

import src.generate_element_data_utils as utils

def _generate_element_data(output='entries'):

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