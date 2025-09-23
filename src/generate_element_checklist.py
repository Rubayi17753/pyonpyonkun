import math, yaml
import pandas as pd
from itertools import chain

import dirs
from src.modules.parser import parse_ids
from src.modules.fetch_config import load_config, fetch_config_chars

def _generate_element_checklist(df):

	def log10(x):
		if x > 0:
			return math.log(x, 10)
		else:
			return -1

	config_data = load_config()
	config_chars = fetch_config_chars(config_data)

	df = df[~(df['element'].isin(config_chars))]

	df['freq2_log'] = df['freq2'].apply(log10)
	df['freq2_log'] = df['freq2_log'].astype(int)
	df = df.groupby(['stroke', 'freq2_log']).agg(elms=('element', list),).reset_index()
	df['elms'] = df['elms'].str.join('')

	df = df.sort_values(by=['stroke', 'freq2_log'], ascending=[True, False])

	return df