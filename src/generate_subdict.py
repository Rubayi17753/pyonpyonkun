import csv, yaml
import pandas as pd
from itertools import chain
from collections import defaultdict
from tqdm import tqdm

from src.generate_element_data import _generate_element_data
from src.modules.parser import parse_ids
from src.modules.idc import idc_all
import dirs

def generate_custom_data():

    print('Loading custom primes and substitutions from yaml')
    with open(dirs.assigned_fp, 'r', encoding='utf-8') as stream:
        docs = yaml.safe_load_all(stream)
        doc0 = next(docs)

        print('Parsing')
        prims = list(chain.from_iterable([parse_ids(chars) for chars in doc0['simplexes'].values()]))
        prims.extend(parse_ids(doc0['simplexes_ignored']))

        prim_to_button = defaultdict(list)
        for keychar, chars in doc0['simplexes'].items():
            if keychar:
                chars = chars.split(';') if ';' in chars else parse_ids(chars)
                for char in chars:
                    prim_to_button[char].append(keychar)

    return prims, prim_to_button
