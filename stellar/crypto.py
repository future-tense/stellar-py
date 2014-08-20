
import hashlib
import pysodium


def sha512half(s):
	m = hashlib.sha512()
	m.update(s)
	digest = m.digest()[0:32]
	return digest


def hash160(s):
	m = hashlib.sha256()
	m.update(s)
	h = m.digest()

	m = hashlib.new('ripemd160')
	m.update(h)
	t = m.digest()
	return t


def sha256hash(s):

	s = s if s else ' '

	m = hashlib.sha256()
	m.update(s)
	hash1 = m.digest()

	m = hashlib.sha256()
	m.update(hash1)
	hash2 = m.digest()
	return hash2


def sign(message, key):
	return pysodium.crypto_sign(message, key)[0:64]


def get_private_key(seed):
	_, sk = pysodium.crypto_sign_seed_keypair(seed)
	return sk


def get_public_key(seed):
	pk, _ = pysodium.crypto_sign_seed_keypair(seed)
	return pk
