import dirs

from src.lint_all import main as lint

from src.preprocess_babelstone import main as main1

from src.readwrite import write_element_data, write_filter_secondary, write_element_checklist
from src.readwrite import write_decompose_all
from src.readwrite_specific import write_element1

if __name__ == '__main__':

	# main1()

	# lint()

	# write_element_data(output='entries', read_from='', write_to='tsv', write_dep=False)
	# write_element_data(fp=dirs.ids_elements_fp_tsv, refresh=True)
	# write_element1()

	write_decompose_all(refresh_element_data=False)
