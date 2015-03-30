
class Fee(object):

	def __init__(self):
		self.default_fee = 10
		self.fee_cushion = 1.2

	def calculate_fee(self):
		return int(self.default_fee * self.fee_scale * self.load_scale)

	def set_fee_scale(self, tx):
		fee_base  = float(tx['fee_base'])
		fee_ref   = float(tx['fee_ref'])
		fee_scale = fee_base / fee_ref
		self.fee_scale = fee_scale

	def set_load_scale(self, tx):
		load_base	 = float(tx['load_base'])
		load_factor  = float(tx['load_factor'])
		load_scale	 = load_factor / load_base
		self.load_scale = load_scale

	def set_initial_fee(self, tx_json):
		result = tx_json['result']
		self.set_fee_scale(result)
		self.set_load_scale(result)
		return self.calculate_fee()

