from address import AccountID, Public, Seed, get_seed_generic
from transaction import *

from decimal import Decimal

from connection_manager import *
import fee


def get_fee():
	return fee.get()


def subscribe_fee():
	fee.subscribe()


def unsubscribe_fee():
	fee.unsubscribe()


def request(command, **kwargs):
	return _getCM().request(command, **kwargs)


def subscribe(**kwargs):
	return _getCM().subscribe(**kwargs)


def unsubscribe(**kwargs):
	return _getCM().unsubscribe(**kwargs)


def add_callback(tx_type, callback):
	_getCM().add_callback(tx_type, callback)


def set_sync_callback(callback):
	_getCM().set_sync_callback(callback)

#-------------------------------------------------------------------------------

_cm = None
def _getCM():
	if _cm is None:
		_cm = ConnectionManager("ws://live.stellar.org:9001/")
		_cm.run()
	return _cm


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


def get_account_info_promise(account_id):

	p = Promise()

	def on_response(js):

		res = js['result']
		if 'account_data' in res:
			ai = res['account_data']
			p.fulfill(ai)
		else:
			error_msg = res['error_message']
			p.reject(Exception(error_msg))

	request('account_info', account=account_id).then(on_response)
	return p


def get_account_info(account_id):
	return get_account_info_promise(account_id).get(timeout=10)


def _parse_amount(m):

	if type(m) != dict:
		m = str(Decimal(m) * 1000000)
	return m
