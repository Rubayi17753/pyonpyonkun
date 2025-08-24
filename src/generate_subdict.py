import csv
from collections import defaultdict
from tqdm import tqdm
from src.parse_string import parse_string_with_unicode

def generate_subdict1():

    subdict = defaultdict(list)

    with open('data/ids_elements.tsv', newline='', encoding='utf-8') as csvfile:
        myreader = csv.reader(csvfile, delimiter='\t')
        rows = list(myreader)
        columns = [list(col) for col in zip(*rows)]

    for char, sub_assigned, sub_alt, sub_ids in tqdm(zip(*columns), desc="Generating subdict"):

        if sub_assigned == ';':
            subdict[char].append(sub_alt)
        elif sub_assigned:
            subdict[char].append(sub_assigned)
        elif sub_assigned == '':
            if '⊖' not in sub_ids:
                subdict[char].append(sub_ids)

    return subdict

def generate_subdict2():

    assignedchar_dict = defaultdict(list)
    subdict = defaultdict(list)

    with open('config/elements.tsv', newline='', encoding='utf-8') as csvfile1:
        myreader = csv.reader(csvfile1, delimiter='\t')
        rows = list(myreader)
        rows = [row for row in rows if row]
        # columns = [list(col) for col in zip(*rows)] 

        for keychar, chars, *_ in rows:
            if keychar:
                for assignedchar in parse_string_with_unicode(chars):
                    assignedchar_dict[assignedchar].append(assignedchar)

    with open('data/ids_elements.tsv', newline='', encoding='utf-8') as csvfile2:
        myreader = csv.reader(csvfile2, delimiter='\t')
        rows = list(myreader)
        columns = [list(col) for col in zip(*rows)]

        for char, sub_assigned, sub_alt, sub_ids, *_ in tqdm(zip(*columns), desc="Generating subdict"):
            
            if char in assignedchar_dict:
                for assignedchar in assignedchar_dict.get(char, list()):
                    subdict[char].append(assignedchar)
            elif char:
                if '⊖' not in sub_ids:
                    subdict[char].append(sub_ids)

    return subdict