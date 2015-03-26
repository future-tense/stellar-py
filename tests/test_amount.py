
import unittest
import stellar


class AmountTest(unittest.TestCase):

	def test_str_currency(self):
		amount = stellar.Amount(1)
		self.assertEqual('STR', amount.currency)

		amount = stellar.Amount(10, 'USD')
		self.assertNotEqual('STR', amount.currency)

	def test_value_normalization(self):
		amount = stellar.Amount('1')
		self.assertEqual('1', amount.value)

		amount = stellar.Amount('1.')
		self.assertEqual('1', amount.value)

		amount = stellar.Amount('1.000')
		self.assertEqual('1', amount.value)

	def test_json_import_str(self):
		amount = stellar.Amount.from_json('1000000')
		self.assertEqual('STR', amount.currency)
		self.assertEqual('1', amount.value)

	def test_json_import_usd(self):
		amount = stellar.Amount.from_json({
			'value':	100,
			'currency':	'USD',
			'issuer':	'issuer'
		})
		self.assertEqual('100', amount.value)
		self.assertEqual('USD', amount.currency)

	def test_json_export_str(self):
		res = stellar.Amount(1).to_json()
		self.assertEqual(res, '1000000')

	def test_json_export_usd(self):
		res = stellar.Amount(1, 'USD', 'issuer').to_json()
		self.assertEqual(res, {
			'value':	'1',
			'currency': 'USD',
			'issuer':	'issuer'
		})
