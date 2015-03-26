
import unittest
import stellar.base58 as base58

_BITCOIN = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


class Base58Test(unittest.TestCase):

	def setUp(self):
		self.base58 = base58.Base58(_BITCOIN)

	def test_encode(self):
		self.assertEqual(
			'W7LcTy7',
			self.base58.encode('\1\2\3\4\5\6')
		)

	def test_decode(self):
		self.assertEqual(
			'\1\2\3\4\5\6',
			self.base58.decode('W7LcTy7')
		)

	def test_encode_check(self):
		self.assertEqual(
			'4HUtbHhPSbmKj',
			self.base58.encode_check('\1\2\3\4\5\6')
		)

	def test_decode_check(self):
		self.assertEqual(
			'\1\2\3\4\5\6',
			self.base58.decode_check('4HUtbHhPSbmKj')
		)

		self.assertRaises(KeyError, self.base58.decode_check, '123456789')
