import os
import re
from tqdm import tqdm
from src.parse_string import parse_string_with_unicode

def interpolate(lis, sublis, N):
    return [*lis[:N], *sublis, *lis[N:]]

def parse_ids(s):

    s = ','.join(parse_string_with_unicode(s))

    if '{' in s:
        for chara in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '{'}:
            if chara in s:
                s = s.replace(f'{chara},', chara)
        s = s.strip(',')     

    return s    
