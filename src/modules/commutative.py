import itertools
import copy

from src.modules.idsi import ids_to_idsi, idsi_to_ids
from src.modules.idc import idc_commutatives

def switch_elements(seq: list):
	return [seq[0], seq[2], seq[1]]

def generate_commutatives(ids: str, include_self=1, non_commutative=1):

	print(ids)

	output = list()
	idsi = ids_to_idsi(ids)

	# print(f'{ids} > {idsi}')

	commutative_seqs = tuple((mykey, myval) for mykey, myval in idsi.items() if myval[0] in idc_commutatives)
	commutative_count = len(commutative_seqs)

	# Examples:
	# togl3 = ((0,0), (0,1), (1,0), (1,1))
	# togl2 = (0,1)
	# togl = 1

	if commutative_count < 1:
		togl3 = ()

		if non_commutative == 0:
			return list()
		elif non_commutative == 1:
			return [ids,]

	elif commutative_count == 1:
		togl3 = ((1,),)
	elif commutative_count == 2:
		togl3 = ((0,1), (1,0), (1,1))
	else:
		togl3 = itertools.product(((0, 1) * commutative_count))
		togl3 = tuple((togl2 for togl2 in togl3 if sum(togl2) != 0))		# Removes (0, 0, ...) from togl3

	for togl2 in togl3:
		idsi_commutative = copy.deepcopy(idsi)
		for ((index, seq), togl) in zip(commutative_seqs, togl2):
			if togl == 1:
				idsi_commutative[index] = switch_elements(seq)

		# print(idsi_commutative)
		output.append(idsi_to_ids(idsi_commutative))
	
	if include_self:
		output.append(ids)
	return output
		





