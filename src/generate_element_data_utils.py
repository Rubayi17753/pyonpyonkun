import pandas as pd
from functools import partial
from itertools import chain

from src.modules.parser import parse_ids
from src.modules.idc import idc_all

import dirs

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

    df['dep_add'] = ''
    df['dep_bin'] = df['dep'].apply(generate_bin)
    df['dep_bin_count'] = df['dep_bin'].apply(sum)
    not_yet_matched = df['dep_bin_count'].sum()
    print(not_yet_matched)

    while not_yet_matched > 0:

        df['dep_add'] = df.apply(sift, axis=1)
        df['dep'] = df['dep'] + df['dep_add']
        df['dep_bin'] = df['dep_bin'].apply(lambda bin: tuple([False for c in bin])) + df['dep_add'].apply(generate_bin)

        '''
        The left half resets the bin (False indicates that a character has been matched, 
                                        and therefore not to be matched again)
        The right half is the new bin
        '''

        df['dep_bin_count'] = df['dep_bin'].apply(sum)
        not_yet_matched = df['dep_bin_count'].sum()
        print(not_yet_matched)

        type_counts = df['dep'].map(type).value_counts()
        print(type_counts)
        exit()

    return df

def read_ids():
    print('Loading IDS')
    df = pd.read_csv(dirs.ids_processed_fp, encoding='utf-8', sep='\t',
                        header=None, names=['unicode', 'chara', 'sub_ids', 'regions', 'ivi'])
    return df

def read_freqlist():
    df = pd.read_csv(dirs.freqlist_fp, encoding='utf-8', sep='\t',
                        header=None, names=['chara', 'freq', 'percentile'])
    return df

def read_strokelist():
    df = pd.read_csv(dirs.strokelist_fp, encoding='utf-8', sep='\t',
                        header=None, names=['unicode', 'chara', 'stroke'])
    df['stroke'] = df['stroke'].fillna(0)
    return df

def _preprocess(df):

	parse_ids_str = partial(parse_ids, mode='str')
	
	print('Deleting entries involving subtraction')
	df = df[~df['sub_ids'].str.contains('㇯', na=False)]

	df['sub_ids'] = df['sub_ids'].copy().apply(parse_ids_str)
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
	df = df.rename(columns={'sub_ids': 'element'})
	return df

def _insert_freq1(df, freqdict):

	print(df['dep'])

	df['freq1'] = df['dep'].apply(lambda cc: [freqdict.get(c, 0) for c in cc])
	df['freq1'] = df['freq1'].apply(sum)
	df = pd.merge(df, read_strokelist().rename(columns={'chara': 'element'}), on='element', how='left')
	return df

def _insert_elm_type(df):

	def get_elm(x):
		if x.startswith('{'):
			return 'unencoded'
		elif x in idc_all:
			return 'idc'
		else:
			return ''
		
	df['elm_type'] = df['element'].apply(get_elm)
	return df

def _insert_dep2(df):
	df_complete = df.copy()
	df_complete = complete_dep(df_complete).rename(columns={'dep': 'dep2'})
	df = pd.merge(df, df_complete, on='element', how='left')
	return df

def _insert_freq2(df, freqdict):

	df['freq2'] = df['dep2'].apply(lambda cc: [freqdict.get(c, 0) for c in cc])
	df['freq2'] = df['freq2'].apply(sum)
	df = pd.merge(df, read_strokelist().rename(columns={'chara': 'element'}), on='element', how='left')
	df['stroke'] = df['stroke'].fillna(0)
	return df

def _insert_freq(df):
	print('Remerge freq_list')
	df = pd.merge(df, read_freqlist(), on='chara', how='left')
	df['freq'] = df['freq'].fillna(0)
	return df

def _insert_sub_ids_regions(df, output):
	df_ids2 = read_ids().copy()
	df_ids2['element'] = df_ids2['element'].fillna('')
	df_ids2['sub_ids'] = df_ids2['sub_ids'].fillna('')
	df_ids2['regions'] = df_ids2['regions'].fillna('')

	if output == 'two_lists':
		df_ids2 = df_ids2.groupby('element').agg(
			sub_ids=('sub_ids', tuple),
			regions=('regions', tuple)).reset_index()

	elif output in {'tuples', 'entries'}:
		df_ids2['sub_ids_regions'] = list(zip(df_ids2['sub_ids'], df_ids2['regions']))
		df_ids2 = df_ids2.groupby('element').agg(sub_ids_regions=('sub_ids_regions', tuple)).reset_index()

	df = pd.merge(df, df_ids2, on='element', how='left')
	return df

def _split_sub_ids_regions(df, output):
	if output == 'entries':
		df = df.explode('sub_ids_regions').reset_index(drop=True)
		df[['sub_ids', 'regions']] = df['sub_ids_regions'].apply(pd.Series)
		return df

def _drop_dupl_and_sort(df):
	df = df.drop_duplicates()
	df = df.sort_values(['elm_type', 'stroke', 'freq1'], ascending=[True, True, False]).reset_index(drop=True)
	return df

def _arrange_cols_(df, output):
	if output in {'entries', 'two_lists'}:
		df = df[['element', 'sub_ids', 'regions', 'elm_type', 'stroke', 'freq', 'freq1', 'freq2', 'dep', 'dep2']]
		df['sub_ids'] = df['sub_ids'].fillna(df['element'])  # default sub_ids: the element itself
		df['regions'] = df['regions'].fillna('.')

	elif output == 'tuples':
		df = df[['element', 'sub_ids_regions', 'elm_type', 'stroke', 'freq', 'freq1', 'freq2', 'dep', 'dep2']]
		df['sub_ids_regions'] = df['sub_ids_regions'].fillna('.')   # wip
	
	return df
