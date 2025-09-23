import pandas as pd
import yaml
from itertools import chain

from src.modules.idc import idc_all
from src.modules.parser import parse_ids
from src.modules.fetch_config import load_config, fetch_config_chars
import dirs

def _filter_secondary(df):
   
    config_data = load_config()
    config_chars = fetch_config_chars(config_data)

    omit_chars = set(list(parse_ids(config_data['simplexes_ignored'])) + list(idc_all))
    pattern = '[' + ''.join(omit_chars) + ']'
    df['sub_ids'] = df['sub_ids'].str.replace(pattern, '', regex=True)
    df = df[
        (df['sub_ids'].str.len() == 1)
        & (df['sub_ids'] != df['element'])
        # & (df['sub_ids'].isin(config_chars))
        & ~(df['element'].isin(config_chars))
    ]
    
    df = df.groupby('sub_ids').agg(secondaries=('element', tuple),).reset_index()
    df = df.rename({'sub_ids': 'primary'})

    return df