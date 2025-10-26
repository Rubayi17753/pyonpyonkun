import dirs

from src.lint_all import main as lint
from src.preprocess_babelstone import main as main1
from src.readwrite import write_element_data, write_filter_secondary, write_element_checklist
from src.readwrite import write_decompose_all
from src.readwrite_specific import write_element1
from src.queries.query_decomp import main as query_decomp
from src.queries.query_dep import main as query_dep

def main():

	prompt_dict = {
				'1': {'desc' : 'decompose all IDSs', 
		  				'action' : lambda: write_decompose_all()},  
				'1_cl': {'desc' : 'generate checklist to aid in elements.yaml (no bearing on rest of code)', 
		   				'action' : lambda: write_element_checklist(fp = dirs.ids_elements_fp_json_lite2)}, 
				'2': {'desc' : 'read elements.yaml & generate element data (json)', 
		   				'action' : lambda: write_element_data(write_fp=dirs.ids_elements_fp_json,
                       output='entries',  
                       write_dep=True,
                       refresh=False)},  
				'2t': {'desc' : 'read elements.yaml & generate element data (tsv)', 
		   				'action' : lambda: write_element_data(write_fp=dirs.ids_elements_fp_tsv,
                       output='entries',  
                       write_dep=False,
                       refresh=False)}, 
				'2a1': {'desc' : 'read elements.yaml & generate element data (json, lite1)', 
		   				'action' : lambda: write_element_data(write_fp=dirs.ids_elements_fp_json_lite1,
                       output='entries',  
                       write_dep=False,
                       refresh=False)}, 
				'2a2': {'desc' : 'read elements.yaml & generate element data (json, lite2)', 
		   				'action' : lambda: write_element_data(fp=dirs.ids_elements_fp_json_lite2, 
                                output='two_lists',
								write_dep=False,
								refresh=False)}, 
				'2b': {'desc' : 'read element data & generate secondaries', 
		   				'action' : lambda: write_filter_secondary(fp = dirs.ids_elements_fp_json)},
				'q1': {'desc' : 'decompose an IDS (query)', 'action' : lambda: query_decomp()}, 
				'q2': {'desc' : "return a character's dependents (query)", 'action' : lambda: query_dep(fp=dirs.ids_elements_fp_json())}, 
				}

	prompts = '\n'.join([f'Enter {k} to {v['desc']}' for k, v in prompt_dict.items()])
	print('Welcome to Pyonpyonkun!')
	print(prompts)
	
	user_input = 'banana'
	while user_input != '':
		user_input = input()
		prompt_dict[user_input]['action']()

if __name__ == '__main__':
	main()
