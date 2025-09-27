import math, yaml
import pandas as pd
import numpy as np
from itertools import chain

import dirs
from src.modules.parser import parse_ids
from src.modules.fetch_prims import load_config, fetch_prims

def _generate_element_checklist(df):

	def log10(x):
		if x > 0:
			return math.log(x, 10)
		else:
			return -1

	prims = fetch_prims()

	df = df[~(df['element'].isin(prims))]

	df['freq2_log'] = df['freq2'].copy().apply(log10)
	df['freq2_log'] = df['freq2_log'].copy().astype(int)

	df['len_ids'] = df['sub_ids'].str.len()
	df['ids_prim'] = np.where(df['len_ids'] <= 1, 'prim', '')

	df = df.groupby(['ids_prim', 'stroke', 'freq2_log']).agg(elms=('element', list),).reset_index()
	df['elms'] = df['elms'].copy().str.join('')

	df = df.sort_values(by=['ids_prim', 'stroke', 'freq2_log'], ascending=[False, True, False])

	return df