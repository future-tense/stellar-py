
import hashlib
import ed25519

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


def sign(message, seed):
	return ed25519.SigningKey(seed).sign(message)[0:64]


def get_private_key(seed):
	pk = ed25519.SigningKey(seed).get_verifying_key().vk_s
	return seed+pk


def get_public_key(seed):
	pk = ed25519.SigningKey(seed).get_verifying_key().vk_s
	return pk
