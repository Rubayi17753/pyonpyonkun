import csv
from tqdm import tqdm

def main():

	data_fp = 'data/babelstone/IDS.TXT'

	with open(data_fp, 'r', encoding='utf-8') as csvfile:
		myreader = csv.reader(csvfile, delimiter='\t')
		# rows = list(myreader)

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

	with open(data_fp.replace('IDS.TXT', 'IDS_preprocessed.tsv'), 'w', encoding='utf-8', newline='') as csvout:
		spamwriter = csv.writer(csvout, delimiter='\t')
		spamwriter.writerows(output)
	
	with open(data_fp.replace('IDS.TXT', 'IDS_comments.tsv'), 'w', encoding='utf-8', newline='') as csvout:
		spamwriter = csv.writer(csvout, delimiter='\t')
		spamwriter.writerows(comments)