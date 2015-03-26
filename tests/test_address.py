
import unittest
import stellar.address as address


MASTERKEY_SEED_BIN = 'DEDCE9CE67B451D852FD4E846FCDE31C4E48EB676DEE37FDC4832DF2167B62D2'.decode('hex')
MASTERKEY_ACCOUNT_BIN = '37B1B26BE3C91C55D51586C3F0E5C4B03E9CEA7F'.decode('hex')

MASTERKEY_ACCOUNT = 'ganVp9o5emfzpwrG5QVUXqMv8AgLcdvySb'
MASTERKEY_SEED = 's3q5ZGX2ScQK2rJ4JATp7rND6X5npG3De8jMbB7tuvm2HAVHcCN'


class AddressTest(unittest.TestCase):

	def test_seed_to_human(self):
		self.assertEqual(
			MASTERKEY_SEED,
			address.seed_to_human(MASTERKEY_SEED_BIN)
		)

	def test_seed_from_human(self):
		self.assertEqual(
			MASTERKEY_SEED_BIN,
			address.seed_from_human(MASTERKEY_SEED)
		)

		self.assertRaises(TypeError, address.seed_from_human, MASTERKEY_ACCOUNT)

	def test_account_to_human(self):
		self.assertEqual(
			MASTERKEY_ACCOUNT,
			address.account_to_human(MASTERKEY_ACCOUNT_BIN)
		)

	def test_account_from_human(self):
		self.assertEqual(
			MASTERKEY_ACCOUNT_BIN,
			address.account_from_human(MASTERKEY_ACCOUNT)
		)
