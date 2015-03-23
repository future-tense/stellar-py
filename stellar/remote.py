
from server import Server

#-------------------------------------------------------------------------------

_optional = {

	'account_currencies': {
		'ledger_index',
		'ledger_hash'
	},

	'account_lines': {
		'peer',
		'ledger_index',
		'ledger_hash'
	},

	'account_tx': {
		'ledger_index_min',
		'ledger_index_max',
		'binary',
		'forward',
		'limit',
		'marker'
	},

	'book_offers': {
		'taker',
		'marker',
		'ledger_index',
		'ledger_hash'
	},

	'ledger': {
		'full',
		'accounts',
		'transactions',
		'expand',
		'ledger_index',
		'ledger_hash'
	},

	'tx': {
		'binary'
	},
}

#-------------------------------------------------------------------------------


class Remote(object):

	def __init__(self, url, async=False):
		"""
			Creates a *Remote* object, connected to a stellard server
			located at *url*. If *async* is True, then all functions that can
			be asynchronous, by default are so.
		"""

		self.server = Server(url)
		self.server.run()
		self.async = async

	def __request(self, command, **kwargs):
		return self.server.request(command, **kwargs)

	def __command(self, command, local):

		def on_result(res):
			return res['result']

		def on_error(err):
			raise Exception(err)

		#	start filling out the kwargs-dict with the required parameters

		skip = {'self', 'kwargs'}
		kwargs = {
			key:val
			for key, val in local.items()
			if key not in skip
		}

		#	if the command has any optional parameters,
		#	add all of the optional parameters that were provided

		if command in _optional:
			for key, val in local['kwargs'].iteritems():
				if key in _optional[command]:
					kwargs[key] = val

		p = self.__request(command, **kwargs).then(on_result, on_error)

		async = self.async
		if 'async' in local['kwargs']:
			async = local['kwargs']['async']

		if async:
			return p
		else:
			return p.get()

	#---------------------------------------------------------------------------

	def cancel(self, promise):
		""" Cancels a promise """

		return self.server.cancel(promise)

	def add_callback(self, tx_type, callback):
		""" Adds a callback to the specified transaction type

		def callback(tx_json):
			...

		"""

		self.server.add_callback(tx_type, callback)

	def set_sync_callback(self, callback):
		""" Set the callback for network status updates

		def callback(status):
			if status:
				#	connected to network
			else:
				#	disconnected from network
		"""

		self.server.set_sync_callback(callback)

	def get_fee(self):
		""" Get the current transaction fee for the remote connection """
		return self.server.get_fee()

	def subscribe_fee(self):
		""" Start subscribing to network fee updates """
		p = self.server.subscribe(streams=['ledger', 'server'])
		p.then(self.server.set_initial_fee)

	def unsubscribe_fee(self):
		""" Stop subscribing to network fee updates """
		self.server.unsubscribe(streams=['ledger', 'server'])

	#---------------------------------------------------------------------------
	#
	#	All of the following methods can be run either synchronously or
	#	asynchronously. If async, they return an aplus promise for further
	#	processing. The default async-status is set in the Remote constructor,
	#	but each of these methods can take an *async* parameter to easily
	#	override the default.
	#
	#---------------------------------------------------------------------------

	def get_account_currencies(self, account, **kwargs):
		""" Lists the currencies an account can send or receive """

		return self.__command('account_currencies', locals())

	def get_account_info(self, account, **kwargs):
		""" Returns information about the given account """

		return self.__command('account_info', locals())

	def get_account_lines(self, account, **kwargs):
		""" Gets a list of all trust lines a particular account is a part of """

		return self.__command('account_lines', locals())

	def get_account_offers(self, account, **kwargs):
		""" Gets a list of all the offers this account has made """

		return self.__command('account_offers', locals())

	def get_account_tx(self, account, **kwargs):
		""" Get a list of transactions that affected this account """

		return self.__command('account_tx', locals())

	def get_book_offers(self, taker_gets, taker_pays, **kwargs):
		""" Returns the offers in a given orderbook """

		return self.__command('book_offers', locals())

	def get_ledger(self, **kwargs):
		""" Gets info about a particular ledger """

		return self.__command('ledger', locals())

	def get_static_path(self, source_account, destination_account, destination_amount, **kwargs):
		""" Finds a path for a transfer """

		return self.__command('static_path_find', locals())

	def get_transaction_entry(self, tx_hash, ledger_index, **kwargs):
		"""
		Get the details of a particular transaction
		from a hash and a ledger index
		"""

		return self.__command('transaction_entry', locals())

	def get_tx(self, transaction, **kwargs):
		""" Get details of a specific transaction """

		return self.__command('tx', locals())

	def get_tx_history(self, start, **kwargs):
		""" Returns the last N transactions starting from the given index """

		return self.__command('tx_history', locals())

	def submit_transaction(self, tx_blob, **kwargs):
		""" Submits a transaction to the network """

		return self.__command('submit', locals())

	def subscribe(self, **kwargs):
		""" Listen to events """

		async = self.async
		if 'async' in kwargs:
			async = kwargs['async']
			del kwargs['async']

		p = self.server.subscribe(**kwargs)

		if async:
			return p
		else:
			return p.get()

	def unsubscribe(self, **kwargs):
		""" Unsubscribe from events that were previously subscribed to """

		async = self.async
		if 'async' in kwargs:
			async = kwargs['async']
			del kwargs['async']

		p = self.server.unsubscribe(**kwargs)

		if async:
			return p
		else:
			return p.get()
