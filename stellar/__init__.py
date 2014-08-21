
from address import AccountID, Public, Seed, get_seed_generic
from federation import *
from ledger import *
from transaction import *


def send_payment(secret, account, destination, amount):

	if not account:
		seed	= Seed.from_human(secret)
		account = AccountID.from_seed(seed).to_human()
	else:
		account = _translate_account_id(account)

	amount = _parse_amount(amount)

	tx_json = {
		'TransactionType': 	'Payment',
		'Account': 			account,
		'Amount': 			amount,
	}

	d = destination.split("?dt=")
	if len(d) == 2:
		tx_json['DestinationTag'] = int(d[1])
	tx_json['Destination'] = _translate_account_id(d[0])

	tx_blob = sign_transaction(secret, tx_json)
	submit_transaction(tx_blob)



def set_regular_key(secret, account, regular_key):

	tx_json = {
		'TransactionType':	'SetRegularKey',
		'Account':			_translate_account_id(account),
		'RegularKey':		_translate_account_id(regular_key),
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


def _translate_account_id(account):

	try:
		t = AccountID.from_human(account)
	except Exception:
		return get_accountid(account)
	else:
		return account
