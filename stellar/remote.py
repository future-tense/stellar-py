
from server import Server

#-------------------------------------------------------------------------------


class Remote(object):

	def __init__(self, url, async=False, callback=None):
		"""
		Creates a *Remote* object, connected to a stellard server
		located at *url*. If *async* is True, then all functions that can
		be asynchronous, by default are so. *callback* is called when the
		network connectivity status is changed.

		def callback(status):
			if status:
				#	connected to network
			else:
				#	disconnected from network
		"""

		self.server = Server(url, callback)
		self.server.run()
		self.async = async

	def __call_filtered(self, func, local):
		""" call func with the filtered local dict as kwargs """

		# filter out variables from local. 'self' for starters.
		# default params that hasn't been set. async, if it's there

		del local['self']

		local = {
			key: val
			for key, val in local.items()
			if val is not None
		}

		async = local.pop('async', self.async)

		def on_result(res):
			return res['result']

		def on_error(err):
			raise Exception(err)

		p = func(**local).then(on_result, on_error)

		return p if async else p.get()

	def __command(self, command, local):

		def func(**kwargs):
			return self.server.request(command, **kwargs)

		return self.__call_filtered(func, local)

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

	def get_account_currencies(
			self,
			account,
			ledger_index=None,
			ledger_hash=None,
			async=None
	):
		""" Lists the currencies an account can send or receive """

		return self.__command('account_currencies', locals())

	def get_account_info(
			self,
			account,
			async=None
	):
		""" Returns information about the given account """

		return self.__command('account_info', locals())

	def get_account_lines(
			self,
			account,
			peer=None,
			ledger_index=None,
			ledger_hash=None,
			async=None
	):
		""" Gets a list of all trust lines a particular account is a part of """

		return self.__command('account_lines', locals())

	def get_account_offers(
			self,
			account,
			async=None
	):
		""" Gets a list of all the offers this account has made """

		return self.__command('account_offers', locals())

	def get_account_tx(
			self,
			account,
			ledger_index_min=None,
			ledger_index_max=None,
			binary=None,
			forward=None,
			limit=None,
			marker=None,
			async=None
	):
		""" Gets a list of transactions that affected this account """

		return self.__command('account_tx', locals())

	def get_book_offers(
			self,
			taker_gets,
			taker_pays,
			taker=None,
			marker=None,
			ledger_index=None,
			ledger_hash=None,
			async=None
	):
		""" Returns the offers in a given orderbook """

		return self.__command('book_offers', locals())

	def get_ledger(
			self,
			full=None,
			accounts=None,
			transactions=None,
			expand=None,
			ledger_index=None,
			ledger_hash=None,
			async=None
	):
		""" Gets info about a particular ledger """

		return self.__command('ledger', locals())

	def get_static_path(
			self,
			source_account,
			destination_account,
			destination_amount,
			async=None
	):
		""" Finds a path for a transfer """

		return self.__command('static_path_find', locals())

	def get_transaction_entry(
			self,
			tx_hash,
			ledger_index,
			async=None
	):
		"""
		Get the details of a particular transaction
		from a hash and a ledger index
		"""

		return self.__command('transaction_entry', locals())

	def get_tx(
			self,
			transaction,
			binary=None,
			async=None
	):
		""" Get details of a specific transaction """

		return self.__command('tx', locals())

	def get_tx_history(
			self,
			start,
			async=None
	):
		""" Returns the last N transactions starting from the given index """

		return self.__command('tx_history', locals())

	def submit_transaction(
			self,
			tx_blob,
			async=None
	):
		""" Submits a transaction to the network """

		return self.__command('submit', locals())

	def subscribe(
			self,
			streams=None,
			accounts=None,
			accounts_rt=None,
			books=None,
			async=None
	):
		""" Listen to events """

		return self.__call_filtered(self.server.subscribe, locals())

	def unsubscribe(
			self,
			streams=None,
			accounts=None,
			accounts_rt=None,
			books=None,
			async=None
	):
		""" Unsubscribe from events that were previously subscribed to """

		return self.__call_filtered(self.server.unsubscribe, locals())
