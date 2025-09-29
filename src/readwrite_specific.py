from src.readwrite import write_element_data

def write_element1():

	df = write_element_data(fp='',
                       output='entries', write_dep=True, refresh=True)
	
	del df['dep']
	df['dep2'] = df['dep2'].copy().apply(lambda x: x[:20])
	df = df.sort_values(['count2',], ascending=[False,]).reset_index(drop=True)  
	df = df[['element', 'sub_ids', 'regions', 'elm_type', 'stroke', 
		'freq2', 
		'count2', 
		'dep2']]
	
	df.to_csv('data/output/ids_elements1.tsv', sep='\t')

	return df