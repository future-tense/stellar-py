import urllib2

import config
import crypto
import address
import serialize
import ledger
from utils import *

#-------------------------------------------------------------------------------

tfFullyCanonicalSig = 0x80000000

HASH_TX_SIGN = 'STX\0'

#-------------------------------------------------------------------------------


def get_signing_hash(blob):
	return crypto.sha512half(HASH_TX_SIGN + blob)


def sign_transaction_blob(seed, blob):

	signing_hash = get_signing_hash(blob)
	key = crypto.get_private_key(seed.data)
	signature = crypto.sign(signing_hash, key)
	return signature


def complete_transaction_fields(tx_json):
	sequence = ledger.get_sequence_number(tx_json['Account'])
	tx_json['Flags'] 		 = tfFullyCanonicalSig
	tx_json['Sequence'] 	 = sequence
	tx_json['Fee'] 			 = 10


def sign_transaction(secret, tx_json):

	seed = address.Seed.from_human(secret)
	pubkey = address.Public.from_seed(seed)
	tx_json['SigningPubKey'] = pubkey.data

	blob = serialize.serialize_json(tx_json)
	signature = sign_transaction_blob(seed, blob)
	tx_json['TxnSignature'] = signature

	tx_blob = serialize.serialize_json(tx_json)
	return to_hex(tx_blob)


def submit_transaction(tx_blob):

	url = config.stellard_url
	data = '{"method":"submit","params":[{"tx_blob":"%s"}]}' % tx_blob

	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)
	res = response.read()
	print res

#-------------------------------------------------------------------------------
