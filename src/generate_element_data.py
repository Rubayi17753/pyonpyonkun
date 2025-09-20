import pandas as pd
from functools import partial
from itertools import chain

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

def complete_dep(df):

    # df = generate_element_data(write_to='', include_dep=True).copy()
    df = df[['element', 'dep']]

    # Removes idem chars in dep and deletes entries with empty elms
    df['dep'] = df.apply(
    lambda row: tuple((x for x in row['dep'] if x != row['element'])),
    axis=1)
    df = df[(df['dep'].str.len() > 0)]

    set_elm = set(df['element']).copy()
    elm_to_dep = pd.Series(df['dep'].values, index=df['element']).to_dict()
    
    def generate_bin(dep):
        return tuple((c in set_elm for c in dep))
    
    def sift(row):
        return tuple(chain.from_iterable((elm_to_dep.get(c, '') for c, bin in zip(row['dep'], row['dep_bin']) if bin == True)))

    df['dep2'] = ''
    df['dep_bin'] = df['dep'].apply(generate_bin)
    df['dep_bin_count'] = df['dep_bin'].apply(sum)
    not_yet_matched = df['dep_bin_count'].sum()
    print(not_yet_matched)

    while not_yet_matched > 0:

        df['dep2'] = df.apply(sift, axis=1)
        df['dep'] = df['dep'] + df['dep2']
        df['dep_bin'] = df['dep_bin'].apply(lambda bin: tuple([False for c in bin])) + df['dep2'].apply(generate_bin)

        '''
        The left half resets the bin (False indicates that a character has been matched, 
                                        and therefore not to be matched again)
        The right half is the new bin
        '''

        df['dep_bin_count'] = df['dep_bin'].apply(sum)
        not_yet_matched = df['dep_bin_count'].sum()
        print(not_yet_matched)

    return df

def _generate_element_data(output='entries', write_to='json', include_dep=False):

    def _preprocess():

        df_ids = read_ids()
        df = df_ids.copy()
        parse_ids_str = partial(parse_ids, mode='str')
        
        print('Deleting entries involving subtraction')
        df = df[~df['sub_ids'].str.contains('㇯', na=False)]

        df['sub_ids'] = df['sub_ids'].apply(parse_ids_str)
        df['sub_ids'] = df['sub_ids'].str.split(',', expand=False)

        return df

    def _insert_char_count(df):
        df['char_count'] = df.groupby('chara')['chara'].transform('count')
        df = df.explode('sub_ids').reset_index(drop=True)
        return df

    # freqdict is based on freq_div (freq / count, to account for chars with more than one IDSs 
    def _freqdict(df):
        df = pd.merge(df, read_freqlist(), on='chara', how='left')
        df['freq_div'] = df['freq']/df['char_count'].fillna(0)
        freqdict = pd.Series(df['freq_div'].values, index=df['chara']).to_dict()
        freqdict = {k: (0 if pd.isna(v) else v) for k, v in freqdict.items()}
        return freqdict

    def _insert_dep(df):
        df = df.groupby('sub_ids').agg(
            dep=('chara', tuple), 
            # freq=('freq_div', 'sum'),
            ).reset_index()
        return df

    def _insert_freq1(df, freqdict=_freqdict(df)):

        df['freq1'] = df['dep'].apply(lambda cc: [freqdict.get(c, 0) for c in cc])
        df['freq1'] = df['freq1'].apply(sum)

        df = df.rename(columns={'sub_ids': 'chara'})
        df = pd.merge(df, read_strokelist(), on='chara', how='left')
        df['stroke'] = df['stroke'].fillna(0)

        return df

    def _insert_elm_type(df):

        def get_elm(x):
            if x.startswith('{'):
                return 'unencoded'
            elif x in idc_all:
                return 'idc'
            else:
                return ''
            
        df['elm_type'] = df['chara'].apply(get_elm)
        return df

    def _insert_dep2(df):
        df_complete = df.copy()
        df_complete = complete_dep(df_complete)
        return df

    def _insert_freq2(df, freqdict=_freqdict(df)):
        ...

    def _insert_freq(df):
        print('Remerge freq_list')
        df = pd.merge(df, read_freqlist(), on='chara', how='left')
        df['freq'] = df['freq'].fillna(0)
        return df

    def _insert_sub_ids_regions(df):
        df_ids2 = read_ids().copy()
        df_ids2['chara'] = df_ids2['chara'].fillna('')
        df_ids2['sub_ids'] = df_ids2['sub_ids'].fillna('')
        df_ids2['regions'] = df_ids2['regions'].fillna('')

        if output == 'two_lists':
            df_ids2 = df_ids2.groupby('chara').agg(
                sub_ids=('sub_ids', tuple),
                regions=('regions', tuple)).reset_index()

        elif output in {'tuples', 'entries'}:
            df_ids2['sub_ids_regions'] = list(zip(df_ids2['sub_ids'], df_ids2['regions']))
            df_ids2 = df_ids2.groupby('chara').agg(sub_ids_regions=('sub_ids_regions', tuple)).reset_index()

        df = pd.merge(df, df_ids2, on='chara', how='left')
        return df

    def _split_sub_ids_regions(df):
        if output == 'entries':
            df = df.explode('sub_ids_regions').reset_index(drop=True)
            df[['sub_ids', 'regions']] = df['sub_ids_regions'].apply(pd.Series)
            return df

    def _final_process1(df):
        df = df.drop_duplicates()
        df = df.sort_values(['elm_type', 'stroke', 'freq1'], ascending=[True, True, False]).reset_index(drop=True)
        df = df.rename(columns={'chara': 'element'})
        return df

    def _write_to_file(df):

        if not include_dep:
            del df['dep']

        if write_to == 'json':
            print(f'Writing to {dirs.ids_elements_fp_json}')
            df.to_json(dirs.ids_elements_fp_json, orient='records', lines=True, force_ascii=False)

        elif write_to == 'csv':
            print(f'Writing to {dirs.ids_elements_fp_csv}')
            df.to_csv(dirs.ids_elements_fp_csv, sep='\t', encoding='utf-8', index=False)

    df = _preprocess()
    df = _insert_char_count(df)
    df = _insert_dep(df)
    df = _insert_freq1(df)
    df = _insert_elm_type(df)
    df = _insert_dep2(df)
    df = _insert_freq2(df)
    df = _insert_freq(df)
    df = _insert_sub_ids_regions(df)
    df = _split_sub_ids_regions(df)
    df = _final_process1(df)
        
    if output in {'entries', 'two_lists'}:
        df = df[['element', 'sub_ids', 'regions', 'elm_type', 'stroke', 'freq', 'freq1', 'freq2', 'dep', 'dep2']]
        df['sub_ids'] = df['sub_ids'].fillna(df['element'])  # default sub_ids: the element itself
        df['regions'] = df['regions'].fillna('.')

    elif output == 'tuples':
        df = df[['element', 'sub_ids_regions', 'elm_type', 'stroke', 'freq', 'freq1', 'freq2', 'dep', 'dep2']]
        df['sub_ids_regions'] = df['sub_ids_regions'].fillna('.')   # wip

    if write_to:
        _write_to_file(df)

    return df

def generate_element_data(output='entries', read_from='x', write_to='json', include_dep=False):

    if read_from == 'x':
        write_to = read_from

    if read_from == 'json':
        try:
            df_sub = pd.read_json(dirs.ids_elements_fp_json, lines=True)
        except FileNotFoundError:
            print(f'{dirs.ids_elements_fp_json} not found. Generating element_data')
            df_sub = _generate_element_data(output, write_to, include_dep)
    
    elif read_from == 'csv':
        try:
            df_sub = pd.read_json(dirs.ids_elements_fp_csv, lines=True)
        except FileNotFoundError:
            print(f'{dirs.ids_elements_fp_csv} not found. Generating element_data')
            df_sub = _generate_element_data(output, include_dep, write_to='csv')

    else:
        df_sub = _generate_element_data(output, write_to, include_dep)

    return df_sub

