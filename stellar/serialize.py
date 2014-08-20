
from address import AccountID
from utils import *

#-------------------------------------------------------------------------------

field_map = {
	'Account':			(8, 1),
	'Amount':			(6, 1),
	'Destination':		(8, 3),
	'DestinationTag':	(2, 14),
	'Fee':				(6, 8),
	'Flags':			(2, 2),
	'RegularKey':		(8, 8),
	'Sequence':			(2, 4),
	'SigningPubKey':	(7, 3),
	'TransactionType':	(1, 2),
	'TxnSignature':		(7, 4),
}

TRANSACTION_TYPES = {
	'Payment': 			0,
	'SetRegularKey':	5,
}

#-------------------------------------------------------------------------------


def serialize_json(tx_json):

	def _comparator(a, b):

		type_a, field_a = field_map[a]
		type_b, field_b = field_map[b]
		if type_a == type_b:
			return field_a - field_b
		else:
			return type_a - type_b

	blob = ''
	keys = sorted(tx_json.keys(), cmp=_comparator)
	for k in keys:
		value = tx_json[k]
		if k == 'TransactionType':
			value = TRANSACTION_TYPES[value]

		type_id, field_id = field_map[k]
		tag = type_id << 4 | field_id
		blob += chr(tag)

		if type_id == 1:
			result = int_to_bytes(value, 2)
			blob += result

		elif type_id == 2:
			result = int_to_bytes(value, 4)
			blob += result

		elif type_id == 6:
			result = int_to_bytes(value, 8)

			top = ord(result[0])
			top &= 0x3f
			if value > 0:
				top |= 0x40
			result = chr(top) + result[1:]
			blob += result

		elif type_id == 7:
			blob += chr(len(value))
			blob += value

		elif type_id == 8:
			t = AccountID.from_human(value)
			blob += chr(len(t.data))
			blob += t.data

	return blob

#-------------------------------------------------------------------------------
