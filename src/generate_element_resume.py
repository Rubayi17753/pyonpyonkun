import math

def _generate_element_summary(df):

	def log10(x):
		return(x, 10)

	df['freq2_log'] = df['freq2'].apply(log10)
	df['freq2_log'] = df['freq2_log'].astype(int)

	df = df.groupby(['stroke', 'freq2_log']).agg(
	elms=('elements', list),
	).reset_index()

	return df