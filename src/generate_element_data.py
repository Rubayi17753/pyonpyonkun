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

def _generate_element_data(output='entries', write_to='json', include_dep=False):

    df_ids = read_ids()
    df = df_ids.copy()
    parse_ids_str = partial(parse_ids, mode='str')
    
    print('Deleting entries involving subtraction')
    df = df[~df['sub_ids'].str.contains('㇯', na=False)]

    df['sub_ids'] = df['sub_ids'].apply(parse_ids_str)
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
        dep=('chara', tuple), 
        # freq=('freq', 'sum'),
        ).reset_index()

    print('Calculating total freqs')
    df['freq1'] = df['dep'].apply(lambda cc: [freqdict.get(c, 0) for c in cc])
    df['freq1'] = df['freq1'].apply(sum)

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

    print('Remerge freq_list')
    df = pd.merge(df, read_freqlist(), on='chara', how='left')
    df['freq'] = df['freq'].fillna(0)

    print('Remerge sub_ids')
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

    if output == 'entries':
        df = df.explode('sub_ids_regions').reset_index(drop=True)
        df[['sub_ids', 'regions']] = df['sub_ids_regions'].apply(pd.Series)

    df = df.drop_duplicates()
    df = df.sort_values(['elm_type', 'stroke', 'freq1'], ascending=[True, True, False]).reset_index(drop=True)
    df = df.rename(columns={'chara': 'element'})

    if output in {'entries', 'two_lists'}:
        df = df[['element', 'sub_ids', 'regions', 'elm_type', 'stroke', 'freq', 'freq1', 'dep']]
        df['sub_ids'] = df['sub_ids'].fillna(df['element'])  # default sub_ids: the element itself
        df['regions'] = df['regions'].fillna('.')

    elif output == 'tuples':
        df = df[['element', 'sub_ids_regions', 'elm_type', 'stroke', 'freq', 'freq1', 'dep']]
        df['sub_ids_regions'] = df['sub_ids_regions'].fillna('.')   # wip

    print(f'include_dep: {include_dep}')

    if not include_dep:
        del df['dep']

    if write_to == 'json':
        print(f'Writing to {dirs.ids_elements_fp_json}')
        df.to_json(dirs.ids_elements_fp_json, orient='records', lines=True, force_ascii=False)

    elif write_to == 'csv':
        print(f'Writing to {dirs.ids_elements_fp_csv}')
        df.to_csv(dirs.ids_elements_fp_csv, sep='\t', encoding='utf-8', index=False)

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

def third_freq():

    df = generate_element_data(write_to='', include_dep=True).copy()
    # df = df.iloc[:1000]
    # df = pd.read_json('data/samples/element_dep.json', lines=True)
    df = df[['element', 'dep']]

    # Removes idem chars in dep and deletes entries with empty elms
    df['dep'] = df.apply(
    lambda row: tuple((x for x in row['dep'] if x != row['element'])),
    axis=1)
    df = df[(df['dep'].str.len() > 0)]

    # print(df.iloc[200:300])
    # exit()

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
    # print(df)

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

    # print(df)
    exit()

    # df_top = df[df['dep_bin_count'] == 0]
    # dict_top= pd.Series(df_top['dep'].values, index=df_top['element']).to_dict()
    
    # mask = df['dep'].apply(lambda dep: all(c in set_elm for c in dep))
    # df_top = df[mask]   # a df of all entries with no dependents in the df
    
    q = '几'    # 几踶
    print(f'len of {dict_top}')
    print(f'len of {q} dep: {len(df.loc[df['element'] == q, 'dep2'].iloc[0])}')
    exit()

    return df

    # print('Expand dep')
    # depx = ('书', '巪', '彐', '為', '為', '爲', '爲', '片', '㔖', '㪲', '㫇', '䎞', '𠀌', '𠀟', '𠁡', '𠁬', '𠃍', '𠄣', '𡧐', '𣪃', '𦭍', '𧰳', '𨾗', '𪢳', '𪥁', '𫤰', '𫼓', '𬊓', '𬊓', '𬲡', '𬲡', '𭀻', '𭀻', '𭁕', '𭆾', '𭓕', '𭓘', '𭠚', '𭥋', '𭩘', '𮞌', '\U000301c8', '\U00030255', '\U00030481', '\U00030912', '\U00030bee', '\U00030bee', '\U00030c2f', '\U00030d97', '\U00030f18', '\U00031d5a', '\U00031d5a')
    # print(expand_dep(depx))
    # df['dep2'] = df['dep'].apply(expand_dep)



