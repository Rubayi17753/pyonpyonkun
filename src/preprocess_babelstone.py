import csv
import pandas as pd
from tqdm import tqdm

import dirs

def main():

	with open(dirs.ids_data_fp, 'r', encoding='utf-8') as tsvfile:
		myreader = csv.reader(tsvfile, delimiter='\t')
		output = list()
		comments = list()
		
		for row in tqdm(myreader):

			if len(row) >= 3 and not row[0].startswith('#'):
				unicode, char, *seqs = row
				tag = ''
				ivi = ''
				
				for seq in seqs:
					if seq.startswith('*'):
						comments.append((unicode, char, seq))

					else:
						if seq.count('$') == 1:
							seq, tag = seq.split('$')
						elif '$' in seq:
							print(seq)
							seq, *tag = seq.split('$')

						seq = seq.lstrip('^')
						tag = tag.lstrip('(').rstrip(')')

						if '〾' in seq:
							seq = seq.replace('〾', '')
							ivi = '〾'
						
						output.append((unicode, char, seq, tag, ivi))

	with open(dirs.ids_processed_fp, 'w', encoding='utf-8', newline='') as tsvout:
		spamwriter = csv.writer(tsvout, delimiter='\t')
		spamwriter.writerows(output)
	
	with open(dirs.ids_comments_fp, 'w', encoding='utf-8', newline='') as tsvout:
		spamwriter = csv.writer(tsvout, delimiter='\t')
		spamwriter.writerows(comments)