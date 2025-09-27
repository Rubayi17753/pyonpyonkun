import dirs
from src.preprocess_babelstone import main as main1
from src.readwrite import write_element_data, write_filter_secondary, write_element_checklist
from src.readwrite import write_decompose_all

if __name__ == '__main__':
	write_filter_secondary()
	# write_element_data(output='entries', read_from='', write_to='tsv', write_dep=False)
	# write_element_data(fp=dirs.ids_elements_fp_tsv, refresh=True)