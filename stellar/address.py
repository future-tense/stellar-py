import os
import crypto
import base58

#-------------------------------------------------------------------------------

VER_SEED			= chr(33)
VER_ACCOUNT_ID		= chr(0)
VER_ACCOUNT_PUBLIC	= chr(67)

#-------------------------------------------------------------------------------


class Address(object):

	def to_human(self):
		s = self.type + self.data
		s = chr(0) + s + four_byte_hash256(s)
		return base58.encode(s)

	@staticmethod
	def from_human(h):
		seed = base58.decode(h)
		check = four_byte_hash256(seed[:-4])
		if check != seed[-4:]:
			raise KeyError
		return seed


class Seed(Address):

	def __init__(self, data):
		self.type = VER_SEED
		self.data = data

	@staticmethod
	def random():
		seed = os.urandom(32)
		return Seed(seed)

	@staticmethod
	def from_human(h):
		seed = Address.from_human(h)
		if seed[0] != VER_SEED:
			raise TypeError
		return Seed(seed[1:-4])


class Public(Address):

	def __init__(self, data):
		self.type = VER_ACCOUNT_PUBLIC
		self.data = data

	@staticmethod
	def from_seed(seed):
		public = crypto.get_public_key(seed.data)
		return Public(public)


class AccountID(Address):

	def __init__(self, data):
		self.type = VER_ACCOUNT_ID
		self.data = data

	@staticmethod
	def from_seed(seed):
		public = Public.from_seed(seed)
		data = crypto.hash160(public.data)
		return AccountID(data)

	@staticmethod
	def from_human(h):
		seed = Address.from_human(h)
		if seed[0] != VER_ACCOUNT_ID:
			raise TypeError
		return AccountID(seed[1:-4])

#-------------------------------------------------------------------------------


def get_seed_generic(s):
	return crypto.sha512half(s)


def four_byte_hash256(s):
	return crypto.sha256hash(s)[0:4]

#-------------------------------------------------------------------------------
