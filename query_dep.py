from src.preprocess_babelstone import main as main1
from src.generate_element_data import generate_element_data

def main():
	df = generate_element_data(read_from='', write_to='')
	char = '㇝'
	print(df.loc[df['element'] == char, 'dep'])
	print(df.loc[df['element'] == char, 'dep2'])

if __name__ == '__main__':
	main()