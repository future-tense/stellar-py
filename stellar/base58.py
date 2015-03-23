
import utils
import crypto

#	_RIPPLE  = 'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'
#	_STELLAR = 'gsphnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCr65jkm8oFqi1tuvAxyz'
#	_BITCOIN = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


BASE = 58


def xlate(v, alphabet):
	return ''.join(alphabet[ch] for ch in v)


def zero_padding(v):

	num_zeroes = 0
	while v[num_zeroes] == '\0':
		num_zeroes += 1
	return '\0' * num_zeroes


def four_byte_hash256(s):
	return crypto.sha256hash(s)[0:4]


class Base58(object):

	def __init__(self, alphabet):
		self.fwd = {chr(i): c for i, c in enumerate(alphabet)}
		self.inv = {c: chr(i) for i, c in enumerate(alphabet)}

	def encode(self, v):
		p = zero_padding(v)
		t = utils.bytes_to_int(v)
		v = utils.int_to_bytes(t, BASE)
		return xlate(p + v, self.fwd)

	def decode(self, v):
		v = xlate(v, self.inv)
		p = zero_padding(v)
		t = utils.bytes_to_int(v, BASE)
		v = utils.int_to_bytes(t)
		return p + v

	def encode_check(self, v):
		c = four_byte_hash256(v)
		return self.encode(v + c)

	def decode_check(self, v):
		v = self.decode(v)
		c = four_byte_hash256(v[:-4])
		if c != v[-4:]:
			raise KeyError
		return v[:-4]
