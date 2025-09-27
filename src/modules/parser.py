import os
import re
from tqdm import tqdm

from src.modules.idc import idc_unarys

def parse_ids(s, mode='list'):

    s = ','.join(tuple(s))

    if '«' in s:
        s = s.replace('«', '{').replace('»', '}')

    if '{' in s:
        for chara in '0123456789{«':
            if chara in s:
                s = s.replace(f'{chara},', chara)
        s = s.strip(',')  

    for unary in idc_unarys:
        if unary in s:
            s = s.replace(f'{unary},', unary)

    if mode == 'list':
        return s.split(',')
    elif mode == 'str':
        return s
