import pandas as pd
import yaml
from itertools import chain

from src.modules.idc import idc_all
from src.modules.parser import parse_ids
import dirs

def load_config():
    with open(dirs.assigned_fp, 'r', encoding='utf-8') as stream:
        docs = yaml.safe_load_all(stream)
        doc0 = next(docs)
        return doc0

def _primary_to_secondary():
	try:
		df = pd.read_json(dirs.secondaries_json_fp, lines=True)
		return pd.Series(df['secondaries'].values, index=df['primary']).to_dict()
	except FileNotFoundError:
		print(f'{dirs.secondaries_json_fp} not found')
		return dict()
	
def fetch_prims(config_data=load_config(), include_presub=True, include_secondary=True):

    df = pd.DataFrame(config_data['simplexes'])

    df_lat_cyp = df[['lat', 'cyp']]
    # lat_to_prim = pd.Series(df_map['cyp'].values, index=df_map['lat']).to_dict()

    df['elms'] = df['elms'].copy().apply(parse_ids)
    df = df.explode('elms').reset_index(drop=True)

    if include_secondary:
        primary_to_secondary = _primary_to_secondary()
        if primary_to_secondary:
            df2 = df.copy()
            df2['secs'] = df2['elms'].map(primary_to_secondary)
            df2 = df2.dropna(subset=['secs'])
            del df2['elms']
            df2 = df2.rename(columns={'secs': 'elms'})
            # df2 = df2.drop_duplicates()
            df2 = df2.explode('elms').reset_index(drop=True)
            df = pd.concat([df, df2])

    prims = df['elms'].to_list()

    df_map = df.copy().groupby('elms').agg(cyp=('cyp', tuple),).reset_index()
    df_prim_cyp = df_map[['cyp', 'elms']]
    # prim_to_cyp = pd.Series(df_map['cyp'].values, index=df_map['elms']).to_dict()

    return prims, df_prim_cyp, df_lat_cyp