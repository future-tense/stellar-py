
from decimal import *


SCALE = 1000000


def clean_up(value):

	v = str(value)
	if '.' in v:
		v = v.rstrip('0')
		if v[-1] == '.':
			v = v[:-1]
	return v


class Amount(object):

	def __init__(self, value, currency='STR', issuer=None):
		self.value		= clean_up(value)
		self.currency	= currency
		self.issuer		= issuer

	@staticmethod
	def from_json(amount):
		if type(amount) == dict:
			return Amount(
				amount['value'],
				amount['currency'],
				amount['issuer']
			)
		else:
			return Amount(str(Decimal(amount) / SCALE))

	def to_json(self):
		if self.currency != 'STR':
			return {
				'value':	self.value,
				'currency':	self.currency,
				'issuer':	self.issuer
			}
		else:
			return str(int(Decimal(self.value) * SCALE))
