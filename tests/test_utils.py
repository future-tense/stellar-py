
import unittest
from stellar import utils


class UtilsTest(unittest.TestCase):

	def test_to_hex(self):
		s = '\01\x0f'
		self.assertEqual('010F', utils.to_hex(s))

	def test_bytes_to_int(self):
		s = '\01\01'
		self.assertEqual(257, utils.bytes_to_int(s, 256))
		self.assertEqual( 17, utils.bytes_to_int(s,  16))

	def test_int_to_bytes(self):
		self.assertEqual('\x01\x0f', utils.int_to_bytes(271))
		self.assertEqual('\x01\x00\x0f', utils.int_to_bytes(271, 16))
		self.assertEqual('\0\0\0\1', utils.int_to_bytes(1, size=4))
