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
    df['elms'] = df['elms'].copy().apply(parse_ids)
    df = df.explode('elms').reset_index(drop=True)

    print(df)
    exit()


    d = [c for c in config_data['simplexes'].values()]
    q = [p['elms'] for p in d]
    # q2 = [(p['key'], p['elms']) for p in d]

    prim_to_key = [(ee, ky) for ky, entry in config_data['simplexes'].items() 
                   for ee in entry['elms']]
    
    print(prim_to_key)
    exit()

    prims = zip(*prim_to_key)[1]

    # prims = set(chain.from_iterable(q))
    # prim_to_key = set(chain.from_iterable(q))

    prims.update(parse_ids(config_data['simplexes_ignored']))
    if include_presub:
        prims.update(parse_ids(config_data['presub'].keys()))
    prims.update(idc_all)

    if include_secondary:
        primary_to_secondary = _primary_to_secondary()

        if primary_to_secondary != dict():
            prims2 = set(chain.from_iterable((primary_to_secondary.get(c, c) for c in prims)))
            prims.update(prims2)

    print(prims)
    exit()

    return prims