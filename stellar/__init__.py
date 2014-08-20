
from address import AccountID, Public, Seed, get_seed_generic
from federation import *
from ledger import *
from transaction import *


def send_payment(secret, account_id, destination, amount):

	if not account_id:
		seed	   = Seed.from_human(secret)
		account_id = AccountID.from_seed(seed).to_human()

	amount = _parse_amount(amount)

	tx_json = {
		'TransactionType': 	'Payment',
		'Account': 			account_id,
		'Amount': 			amount,
	}

	d = destination.split("?dt=")
	if len(d) == 2:
		tx_json['DestinationTag'] = int(d[1])
	tx_json['Destination'] = d[0]

	tx_blob = sign_transaction(secret, tx_json)
	submit_transaction(tx_blob)


def set_regular_key(secret, account_id, regular_key):

	tx_json = {
		'TransactionType':	'SetRegularKey',
		'Account':			account_id,
		'RegularKey':		regular_key,
	}

	tx_blob = sign_transaction(secret, tx_json)
	submit_transaction(tx_blob)


def _parse_amount(m):

	if not '.' in m:
		m = int(m) * 1000000
	else:
		i, f = m.split('.')
		m = int(i + f)
		m *= 1000000
		m /= 10 ** len(f)
	return m
