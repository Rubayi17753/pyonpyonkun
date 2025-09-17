import csv, yaml
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

from src.modules.parser import parse_ids
from src.modules.idc import idc_all
import dirs

def read_ids():
    print('Loading IDS')
    df = pd.read_csv(dirs.ids_processed_fp, encoding='utf-8', sep='\t',
                        header=None, names=['unicode', 'chara', 'sub_ids', 'regions', 'ivi'])
    return df

def read_freqlist():
    print('Loading freqlist')
    df = pd.read_csv(dirs.freqlist_fp, encoding='utf-8', sep='\t',
                        header=None, names=['chara', 'freq', 'percentile'])
    return df

def read_strokelist():
    print('Loading strokelist')
    df = pd.read_csv(dirs.strokelist_fp, encoding='utf-8', sep='\t',
                        header=None, names=['unicode', 'chara', 'stroke'])
    return df

def generate_assignedchar_data():

    assignedchar_data = defaultdict(list)
    subdict = defaultdict(list)
    with open(dirs.elements_fp, 'r', encoding='utf-8') as stream:
        docs = yaml.safe_load_all(stream)
        doc0 = next(docs)

        for keychar, chars in doc0['simplexes'].items():
            if keychar:
                if ' ' in chars:
                    chars = chars.split(' ')
                else:
                    chars = parse_ids(chars)
                for assignedchar in chars:
                    assignedchar_data[assignedchar].append(assignedchar)

    return assignedchar_data

def generate_element_data():

    df_ids = read_ids()
    df = df_ids.copy()
    
    print('Deleting entries involving subtraction')
    df = df[~df['sub_ids'].str.contains('㇯', na=False)]

    df['sub_ids'] = df['sub_ids'].apply(parse_ids)
    df['sub_ids'] = df['sub_ids'].str.split(',', expand=False)

    print('Introducing charcount, explode')
    df['char_count'] = df.groupby('chara')['chara'].transform('count')
    df = df.explode('sub_ids').reset_index(drop=True)

    # print(df[df['char_count'] > 1])

    print('Introducing freqlist')
    df = pd.merge(df, read_freqlist(), on='chara', how='left')
    df['freq'] = df['freq']/df['char_count'].fillna(0)
    freqdict = pd.Series(df['freq'].values, index=df['chara']).to_dict()
    freqdict = {k: (0 if pd.isna(v) else v) for k, v in freqdict.items()}

    df = df.groupby('sub_ids').agg(
        chars=('chara', tuple), 
        # freq=('freq', 'sum'),
        ).reset_index()
    
    print('Calculating total freqs')
    df['freq'] = df['chars'].apply(lambda cc: [freqdict.get(c, 0) for c in cc])
    df['freq'] = df['freq'].apply(sum)

    df = df.rename(columns={'sub_ids': 'chara'})
    df = pd.merge(df, read_strokelist(), on='chara', how='left')
    df['stroke'] = df['stroke'].fillna(0)

    print('Introducing elm_type')
    def get_elm(x):
        if x.startswith('{'):
            return 'unencoded'
        elif x in idc_all:
            return 'idc'
        else:
            return ''
    df['elm_type'] = df['chara'].apply(get_elm)

    df = df.drop_duplicates()
    df = df.sort_values(['elm_type', 'stroke', 'freq'], ascending=[True, True, False]).reset_index(drop=True)
    df = df[['chara', 'elm_type', 'freq', 'stroke']]
    df.columns = ['element', 'elm_type', 'freq', 'stroke']

    print(f'Writing to {dirs.ids_elements_fp}')
    df.to_csv(dirs.ids_elements_fp, sep='\t', encoding='utf-8', index=False)
    return df

def generate_subdict(assignedchar_data):

    subdict = defaultdict()

    df_ids = pd.read_csv(dirs.ids_processed_fp, encoding='utf-8', 
                    header=None, names=['unicode', 'chara', 'sub_ids', 'regions', 'ivi'])
    
    with open(dirs.ids_processed_fp, newline='', encoding='utf-8') as csvfile2:
        myreader = csv.reader(csvfile2, delimiter='\t')
        rows = list(myreader)
        columns = [list(col) for col in zip(*rows)]

        for unicode, char, sub_ids, *_ in tqdm(zip(*columns), desc="Generating subdict"):
            
            if char in assignedchar_data:
                for assignedchar in assignedchar_data.get(char, list()):
                    subdict[char].append(assignedchar)
            elif char:
                if '⊖' not in sub_ids:
                    subdict[char].append(sub_ids)

    return subdict