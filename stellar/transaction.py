
import crypto
import address
import serialize
import ledger
from connection_manager import *
from utils import *

from aplus import Promise, listPromise
import math

#-------------------------------------------------------------------------------

tfFullyCanonicalSig = 0x80000000

HASH_TX_SIGN = 'STX\0'

#-------------------------------------------------------------------------------

default_fee = 10
fee_cushion = 1.5

#-------------------------------------------------------------------------------


def transaction_fee_promise():

	p = Promise()

	def on_server_response(res):

		server, ledger = res
		res1 = server['result']
		res2 = ledger['result']

		factor  = float(res1['load_factor']) / float(res1['load_base'])
		factor *= float(res2['fee_base'])    / float(res2['fee_ref'])
		factor *= fee_cushion
		fee = int(math.ceil(default_fee * factor))
		p.fulfill(fee)

	p1 = cm.send_command('subscribe', streams=['server'])
	p2 = cm.send_command('subscribe', streams=['ledger'])
	listPromise([p1, p2]).done(on_server_response)

	cm.send_command('unsubscribe', streams=['server']).done()
	cm.send_command('unsubscribe', streams=['ledger']).done()

	return p


def transaction_fields_completed_promise(tx_json):

	p = Promise()

	def inner(res):
		sequence, fee = res
		tx_json['Flags']	= tfFullyCanonicalSig
		tx_json['Sequence']	= sequence
		tx_json['Fee']		= fee
		p.fulfill(tx_json)

	p1 = ledger.get_sequence_number_promise(tx_json['Account'])
	p2 = transaction_fee_promise()
	listPromise([p1, p2]).then(inner)

	return p


def transaction_submitted_promise(tx_blob):

	p = Promise()

	def on_response(js):
		res = js['result']
		p.fulfill((res['engine_result'], res['engine_result_message']))

	cm.send_command('submit', tx_blob=tx_blob).then(on_response)
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
	return transaction_fields_completed_promise(tx_json).get(timeout=10)


def submit_transaction(tx_blob):
	return transaction_submitted_promise(tx_blob).get(timeout=10)

#-------------------------------------------------------------------------------
