
import stellar
import crypto
import address
import serialize
from utils import *

from aplus import Promise

#-------------------------------------------------------------------------------

tfFullyCanonicalSig = 0x80000000

HASH_TX_SIGN = 'STX\0'

#-------------------------------------------------------------------------------


def transaction_fields_completed_promise(tx_json):

	p = Promise()

	if 'Flags' in tx_json:
		tx_json['Flags'] |= tfFullyCanonicalSig
	else:
		tx_json['Flags'] = 0

	tx_json['Fee'] = stellar.get_fee()

	if 'Sequence' in tx_json:
		p.fulfill(tx_json)
	else:
		def inner(res):
			tx_json['Sequence'] = res['Sequence']
			p.fulfill(tx_json)

		p = stellar.get_account_info_promise(tx_json['Account'])
		p.then(inner)

	return p


def transaction_submitted_promise(tx_blob):

	p = Promise()

	def on_response(js):
		res = js['result']
		p.fulfill((res['engine_result'], res['engine_result_message']))

	stellar.request('submit', tx_blob=tx_blob).then(on_response)
	return p

#-------------------------------------------------------------------------------


def get_signing_hash(blob):
	return crypto.sha512half(HASH_TX_SIGN + blob)


def sign_transaction_blob(seed, blob):

	signing_hash = get_signing_hash(blob)
	key = crypto.get_private_key(seed.data)
	signature = crypto.sign(signing_hash, key)
	return signature


def sign_transaction(secret, tx_json):

	seed = address.Seed.from_human(secret)
	pubkey = address.Public.from_seed(seed)
	tx_json['SigningPubKey'] = pubkey.data

	blob = serialize.serialize_json(tx_json)
	signature = sign_transaction_blob(seed, blob)
	tx_json['TxnSignature'] = signature

	tx_blob = serialize.serialize_json(tx_json)
	return to_hex(tx_blob)


def complete_transaction_fields(tx_json):
	transaction_fields_completed_promise(tx_json).wait()


def submit_transaction(tx_blob):
	return transaction_submitted_promise(tx_blob).get(timeout=20)

#-------------------------------------------------------------------------------
