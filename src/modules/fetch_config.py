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
		df = pd.read_json(dirs.secondaries_json_fp)
		return pd.Series(df['secondaries'].values, index=df['primary']).to_dict()
	except:
		return dict()
	
def fetch_prims(config_data=load_config(), include_compounds=True, include_secondary=True):

    prims = set(chain.from_iterable((parse_ids(chars) for chars in config_data['simplexes'].values())))
    prims.update(parse_ids(config_data['simplexes_ignored']))
    if include_compounds:
        prims.update(parse_ids(config_data['compounds'].keys()))
    prims.update(idc_all)

    if include_secondary:
        primary_to_secondary = _primary_to_secondary()
        if primary_to_secondary != dict():
            prims = list(((primary_to_secondary.get(c, c) for c in prims)))

    return prims