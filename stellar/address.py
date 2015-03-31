
import stellar.base58
import crypto

#-------------------------------------------------------------------------------

_STELLAR = 'gsphnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCr65jkm8oFqi1tuvAxyz'

_VER_SEED			= chr(33)
_VER_ACCOUNT_ID		= chr(0)
_VER_ACCOUNT_PUBLIC	= chr(67)

#-------------------------------------------------------------------------------

base58 = stellar.base58.Base58(_STELLAR)

#-------------------------------------------------------------------------------


def to_human(version, data):
	return base58.encode_check(version + data)


def from_human(version, h):
	seed = base58.decode_check(h)
	if seed[0] != version:
		raise TypeError

	return seed[1:]


def account_to_human(account):
	return to_human(_VER_ACCOUNT_ID, account)


def account_from_human(account):
	return from_human(_VER_ACCOUNT_ID, account)


def seed_to_human(seed):
	return to_human(_VER_SEED, seed)


def seed_from_human(seed):
	return from_human(_VER_SEED, seed)


def account_from_seed(secret):

	seed = seed_from_human(secret)
	public_key = crypto.get_public_key(seed)
	account = crypto.hash160(public_key)
	account = account_to_human(account)
	return account


#-------------------------------------------------------------------------------
