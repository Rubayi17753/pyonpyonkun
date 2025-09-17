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
    df_ids2['ids_tuples'] = df_ids2['sub_ids'] + '`' + df_ids2['regions']

    df_ids2 = df_ids2.groupby('chara').agg(ids_tuples=('ids_tuples', tuple)).reset_index()
    df = pd.merge(df, df_ids2, on='chara', how='left')
    df = df.explode('ids_tuples').reset_index(drop=True)
    df[['ids_tuples', 'regions']] = df['ids_tuples'].str.split('`', expand=True)

    df = df.drop_duplicates()
    df = df.sort_values(['elm_type', 'stroke', 'freq1'], ascending=[True, True, False]).reset_index(drop=True)
    df = df[['chara', 'ids_tuples', 'regions', 'elm_type', 'stroke', 'freq', 'freq1']]
    df.columns = ['element', 'ids_tuples', 'regions', 'elm_type', 'stroke', 'freq', 'freq1']

    print(f'Writing to {dirs.ids_assigned_fp}')
    df.to_csv(dirs.ids_assigned_fp, sep='\t', encoding='utf-8', index=False)
    return df

def generate_assignedchar_data():

    assignedchar_data = defaultdict(list)
    subdict = defaultdict(list)
    with open(dirs.assigned_fp, 'r', encoding='utf-8') as stream:
        docs = yaml.safe_load_all(stream)
        doc0 = next(docs)

        print('Generating assignedchar_data')
        for keychar, chars in doc0['simplexes'].items():
            if keychar:
                if ' ' in chars:
                    chars = chars.split(' ')
                else:
                    chars = parse_ids(chars)
                for assignedchar in chars:
                    assignedchar_data[assignedchar].append(assignedchar)

    return assignedchar_data

def third_freq(df):

    print('Extract dict_comp')
    df_comp = df.copy()
    dict_comp = pd.Series(df_comp['dep'].values, index=df_comp['element']).to_dict()

    def expand_dep(dep):

        dep_prev = tuple(dep)
        dep = list()
        for char in dep_prev:
            match = dict_comp.get(char, '')
            if match:
                if char != match:
                    dep.extend(match)

        if dep != dep_prev:
            print(dep)
            expand_dep(dep)

    print('Expand dep')
    # depx = ('书', '巪', '彐', '為', '為', '爲', '爲', '片', '㔖', '㪲', '㫇', '䎞', '𠀌', '𠀟', '𠁡', '𠁬', '𠃍', '𠄣', '𡧐', '𣪃', '𦭍', '𧰳', '𨾗', '𪢳', '𪥁', '𫤰', '𫼓', '𬊓', '𬊓', '𬲡', '𬲡', '𭀻', '𭀻', '𭁕', '𭆾', '𭓕', '𭓘', '𭠚', '𭥋', '𭩘', '𮞌', '\U000301c8', '\U00030255', '\U00030481', '\U00030912', '\U00030bee', '\U00030bee', '\U00030c2f', '\U00030d97', '\U00030f18', '\U00031d5a', '\U00031d5a')
    # print(expand_dep(depx))
    df['dep2'] = df['dep'].apply(expand_dep)

def generate_subdict():

    subdict = defaultdict()
    assignedchar_data = generate_assignedchar_data()

    df_ids = pd.read_csv(dirs.ids_processed_fp, encoding='utf-8', 
                    header=None, names=['unicode', 'chara', 'sub_ids', 'regions', 'ivi'])
    
    print(assignedchar_data)
    exit()
    
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