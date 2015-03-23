
import os
import crypto
import serialize
from stellar import utils, address


def generate_keypair():
	""" Generate an address and a secret key """

	seed = os.urandom(32)
	public_key = crypto.get_public_key(seed)
	account = crypto.hash160(public_key)
	account = address.account_to_human(account)
	seed    = address.seed_to_human(seed)
	return account, seed

#-------------------------------------------------------------------------------

_HASH_TX_SIGN = 'STX\0'

#-------------------------------------------------------------------------------


def _get_signing_hash(blob):
	return crypto.sha512half(_HASH_TX_SIGN + blob)


def _sign_blob(tx_blob, seed):

	signing_hash = _get_signing_hash(tx_blob)
	signature = crypto.sign(signing_hash, seed)
	return signature


def sign(tx_json, secret):
	""" Signs a transaction with the secret and returns a tx_blob """

	seed = address.seed_from_human(secret)
	pubkey = crypto.get_public_key(seed)
	tx_json['SigningPubKey'] = pubkey

	tx_blob = serialize.serialize_json(tx_json)
	signature = _sign_blob(tx_blob, seed)
	tx_json['TxnSignature'] = signature

	tx_blob = serialize.serialize_json(tx_json)
	return utils.to_hex(tx_blob)
