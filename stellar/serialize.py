from address import AccountID
from utils import *
from decimal import Decimal

#-------------------------------------------------------------------------------

field_map = {
	'Account':			(8, 1),
	'Amount':			(6, 1),
	'ClearFlag':		(2, 34),
	'Destination':		(8, 3),
	'DestinationTag':	(2, 14),
	'Fee':				(6, 8),
	'Flags':			(2, 2),
	'InflationDest':	(8, 9),
	'LimitAmount':		(6, 3),
	'OfferSequence':	(2, 25),
	'Paths':			(18, 1),
	'RegularKey':		(8, 8),
	'SendMax':			(6, 9),
	'Sequence':			(2, 4),
	'SetFlag':			(2, 33),
	'SigningPubKey':	(7, 3),
	'TakerGets':		(6, 5),
	'TakerPays':		(6, 4),
	'TransactionType':	(1, 2),
	'TransferRate':		(2, 11),
	'TxnSignature':		(7, 4),
}

TRANSACTION_TYPES = {
	'AccountSet':		3,
	'OfferCancel':		8,
	'OfferCreate':		7,
	'Payment': 			0,
	'SetRegularKey':	5,
	'TrustSet':			20
}


#-------------------------------------------------------------------------------


def parse_non_native_amount(string):

	amount	 = Decimal(string).normalize()
	parts	 = amount.as_tuple()
	exponent = parts.exponent

	value = ''.join(map(str, parts.digits))
	exponent += len(value)

	value = value.ljust(16, '0')
	exponent -= 16

	value = int(value)
	if value == 0:
		exponent = -100

	return parts.sign, value, exponent


def serialize_non_native_amount(amount):

	negative, value, exponent = parse_non_native_amount(amount)

	hi = 1 << 31
	if value and not negative:
		hi |= 1 << 30
	hi |= ((97 + exponent) & 0xff) << 22

	value |= hi << 32
	return int_to_bytes(value, 8)


def serialize_currency(currency):

	if currency == 'STR':
		data = 20 * chr(0)
	else:
		data = 12 * chr(0) + currency + 5 * chr(0)
	return data


def serialize_native_amount(amount):

	amount = int(amount)
	result = int_to_bytes(amount, 8)

	top = ord(result[0])
	top &= 0x3f
	if amount > 0:
		top |= 0x40
	result = chr(top) + result[1:]
	return result


def serialize_account_id(human):
	return AccountID.from_human(human).data


def serialize_amount(value):

	blob = ''
	if type(value) == dict:
		blob += serialize_non_native_amount(value['value'])
		blob += serialize_currency(value['currency'])
		blob += serialize_account_id(value['issuer'])
	else:
		blob += serialize_native_amount(value)
	return blob


def serialize_account(value):
	blob = ''
	data = serialize_account_id(value)
	blob += chr(len(data))
	blob += data
	return blob


def serialize_pathset(value):
	path_boundary	= chr(0xff)
	path_end		= chr(0x00)
	flag_account	= 0x01
	flag_currency	= 0x10
	flag_issuer		= 0x20

	blob = ''
	for index, path in enumerate(value):

		if index != 0:
			blob += path_boundary

		for entry in path:
			flags = 0
			if 'account' in entry:
				flags |= flag_account
			if 'currency' in entry:
				flags |= flag_currency
			if 'issuer' in entry:
				flags |= flag_issuer
			if entry['type'] != flags:
				#raise hell
				pass

			flags = entry['type']
			blob += chr(flags)
			if flags & flag_account:
				blob += serialize_account_id(entry['account'])
			if flags & flag_currency:
				blob += serialize_currency(entry['currency'])
			if flags & flag_issuer:
				blob += serialize_account_id(entry['issuer'])

	blob += path_end
	return blob


def serialize_int16(value):
	return int_to_bytes(value, 2)


def serialize_int32(value):
	return int_to_bytes(value, 4)


def serialize_vl(value):
	blob = ''
	blob += chr(len(value))
	blob += value
	return blob

#-------------------------------------------------------------------------------

serializer_dict = {
	1: serialize_int16,
	2: serialize_int32,
	6: serialize_amount,
	7: serialize_vl,
	8: serialize_account,
	18: serialize_pathset,
}

#-------------------------------------------------------------------------------


def serialize_json(tx_json):

	def _comparator(a, b):
		return 1 if field_map[a] > field_map[b] else -1

	blob = ''
	keys = sorted(tx_json.keys(), cmp=_comparator)
	for k in keys:
		value = tx_json[k]
		if k == 'TransactionType':
			value = TRANSACTION_TYPES[value]

		type_id, field_id = field_map[k]
		tag = ((type_id << 4 if type_id < 16 else 0) |
			   (field_id if field_id < 16 else 0))
		blob += chr(tag)

		if type_id >= 16:
			blob += chr(type_id)
		if field_id >= 16:
			blob += chr(field_id)

		if type_id in serializer_dict:
			blob += serializer_dict[type_id](value)

	return blob

#-------------------------------------------------------------------------------
