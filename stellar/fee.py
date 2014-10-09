import stellar

_fee_structure = {
	'default_fee': 10,
	'fee_cushion': 1.2,
}


def set_fee_scale(tx):
	fee_base  = float(tx['fee_base'])
	fee_ref   = float(tx['fee_ref'])
	fee_scale = fee_base / fee_ref
	_fee_structure['fee_scale']  = fee_scale


def set_load_scale(tx):
	load_base	 = float(tx['load_base'])
	load_factor  = float(tx['load_factor'])
	load_scale	 = load_factor / load_base
	_fee_structure['load_scale'] = load_scale


def get():
	f = _fee_structure
	return int(f['default_fee'] * f['fee_scale'] * f['load_scale'])


def subscribe():

	def set_initial_fee(tx_json):
		result = tx_json['result']
		set_fee_scale(result)
		set_load_scale(result)

	p = stellar.subscribe(streams=['ledger', 'server'])
	p.then(set_initial_fee)


def unsubscribe():
	stellar.unsubscribe(streams=['ledger', 'server'])
