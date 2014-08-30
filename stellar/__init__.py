
from address import AccountID, Public, Seed, get_seed_generic
from ledger import *
from transaction import *
from connection_manager import *


def generate_keypair(password=None):

	if password:
		seed = get_seed_generic(password)
		seed = Seed(seed)
	else:
		seed = Seed.random()

	account		= AccountID.from_seed(seed).to_human()
	secret_key = seed.to_human()
	return account, secret_key


def get_payment_tx_json(account, destination, amount):

	amount = _parse_amount(amount)

	tx_json = {
		'TransactionType': 	'Payment',
		'Account': 			account,
		'Amount': 			amount,
	}

	d = destination.split("?dt=")
	if len(d) == 2:
		tx_json['DestinationTag'] = int(d[1])
	tx_json['Destination'] = d[0]

	complete_transaction_fields(tx_json)
	return tx_json


def send_payment(secret, account, destination, amount):

	if not account:
		seed	= Seed.from_human(secret)
		account = AccountID.from_seed(seed).to_human()

	try:
		tx_json = get_payment_tx_json(account, destination, amount)
	except Exception as e:
		return e[0], e[1]

	tx_blob = sign_transaction(secret, tx_json)
	return submit_transaction(tx_blob)


def set_regular_key(secret, account, regular_key):

	tx_json = {
		'TransactionType':	'SetRegularKey',
		'Account':			account,
		'RegularKey':		regular_key,
	}

	try:
		complete_transaction_fields(tx_json)
	except Exception as e:
		return e[0], e[1]

	tx_blob = sign_transaction(secret, tx_json)
	return submit_transaction(tx_blob)


def _parse_amount(m):

	if not '.' in m:
		m = int(m) * 1000000
	else:
		i, f = m.split('.')
		m = int(i + f)
		m *= 1000000
		m /= 10 ** len(f)
	return m
