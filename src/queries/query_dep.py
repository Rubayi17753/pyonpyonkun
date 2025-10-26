from src.preprocess_babelstone import main as main1
from src.readwrite import write_element_data
import pandas as pd, dirs

def main(fp=dirs.ids_elements_fp_json):

	try:
		df = pd.read_json(fp, lines=True)
	except FileNotFoundError:
		print(f'{fp} not found. Generating element_data')
		df = write_element_data(fp,
					   output='entries',  
					   write_dep=False,
						refresh=False)

	char = None
	while char != '':
		char = input('Enter char (or press Enter to quit)\n')
		print(df.loc[df['element'] == char, 'dep'])
		print(df.loc[df['element'] == char, 'dep2'])

if __name__ == '__main__':
	main()