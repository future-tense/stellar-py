
from aplus import listPromise

from server import Server
import transaction
import local
import address

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

		# filter out variables from local

		del local['self']
		async = local.pop('async')
		local.update(local.pop('kwargs', {}))

		def on_result(res):
			return res['result']

		def on_error(err):
			raise Exception(err)

		async = async if async else self.async
		p = func(**local).then(on_result, on_error)
		return p if async else p.get()

	def __command(self, command, local):

		def func(**kwargs):
			return self.server.request(command, **kwargs)

		return self.__call_filtered(func, local)

	def __hl_command(self, account, on_success, async):
		seq = self.get_sequence_number(account, async=True)
		fee = self.get_fee(async=True)
		p = listPromise([seq, fee]).then(on_success)
		async = async if async else self.async
		return p if async else p.get()

	#---------------------------------------------------------------------------

	def cancel(self, promise):
		""" Cancels a promise """

		self.server.cancel(promise)

	def add_callback(self, tx_type, callback):
		""" Adds a callback to the specified transaction type

		def callback(tx_json):
			...
		"""

		self.server.add_callback(tx_type, callback)

	#---------------------------------------------------------------------------
	#
	#	All of the following methods can be run either synchronously or
	#	asynchronously. If async, they return an aplus promise for further
	#	processing. The default async-status is set in the Remote constructor,
	#	but each of these methods can take an *async* parameter to easily
	#	override the default.
	#
	#---------------------------------------------------------------------------

	def get_fee(self, async=None):
		""" Get the current transaction fee for the remote connection """

		async = async if async else self.async
		p = self.server.fee_promise
		return p if async else p.get()

	def get_sequence_number(self, account, async=None):
		""" Get the current sequence number for this account """

		def get_seq(res):
			return res['account_data']['Sequence']

		async = async if async else self.async
		p = self.get_account_info(account, async=True).then(get_seq)
		return p if async else p.get()

	def create_find_path(
			self,
			source_account,
			destination_account,
			destination_amount,
			callback,
			async=None,
			**kwargs
	):
		""" Creates a find_path_session """

		local = locals()
		local['subcommand'] = 'create'
		callback = local.pop('callback')
		self.server.set_path_callback(callback)

		return self.__command('find_path', local)

	def close_find_path(self, async=None):
		""" Closes a find_path session """

		subcommand = 'close'
		return self.__command('find_path', locals())

	def get_account_currencies(
			self,
			account,
			async=None,
			**kwargs
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
			async=None,
			**kwargs
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
			async=None,
			**kwargs
	):
		""" Gets a list of transactions that affected this account """

		return self.__command('account_tx', locals())

	def get_book_offers(
			self,
			taker_gets,
			taker_pays,
			async=None,
			**kwargs
	):
		""" Returns the offers in a given orderbook """

		return self.__command('book_offers', locals())

	def get_ledger(
			self,
			async=None,
			**kwargs
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
			async=None,
			**kwargs
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
			async=None,
			**kwargs
	):
		""" Listen to events """

		return self.__call_filtered(self.server.subscribe, locals())

	def unsubscribe(
			self,
			async=None,
			**kwargs
	):
		""" Unsubscribe from events that were previously subscribed to """

		return self.__call_filtered(self.server.unsubscribe, locals())

	#---------------------------------------------------------------------------

	def cancel_offer(self, secret, account, offer_sequence, async=None):
		""" Cancels a previously issued offer. """

		if not account:
			account = address.account_from_seed(secret)

		def on_success(res):
			seq, fee = res
			tx_json = transaction.offer_cancel(
				account,
				offer_sequence,
				seq,
				fee
			)
			tx_blob = local.sign(tx_json, secret)
			return self.submit_transaction(tx_blob, async=True)

		return self.__hl_command(account, on_success, async)

	def create_offer(self, secret, account, taker_gets, taker_pays,
					 async=None, **kwargs):
		""" Creates an offer to trade. """

		if not account:
			account = address.account_from_seed(secret)

		def on_success(res):
			seq, fee = res
			tx_json = transaction.offer_create(
				account,
				taker_gets,
				taker_pays,
				seq,
				fee,
				**kwargs
			)
			tx_blob = local.sign(tx_json, secret)
			return self.submit_transaction(tx_blob, async=True)

		return self.__hl_command(account, on_success, async)

	def merge_accounts(self, secret, account, destination, async=None):
		""" Merges an account into a destination account. """

		if not account:
			account = address.account_from_seed(secret)

		def on_success(res):
			seq, fee = res
			tx_json = transaction.account_merge(
				account,
				destination,
				seq,
				fee
			)
			tx_blob = local.sign(tx_json, secret)
			return self.submit_transaction(tx_blob, async=True)

		return self.__hl_command(account, on_success, async)

	def send_payment(self, secret, account, destination, amount,
					 async=None, **kwargs):
		""" Sends a payment to a destination account. """

		if not account:
			account = address.account_from_seed(secret)

		def on_success(res):
			seq, fee = res
			tx_json = transaction.payment(
				account,
				destination,
				amount,
				seq,
				fee,
				**kwargs
			)
			tx_blob = local.sign(tx_json, secret)
			return self.submit_transaction(tx_blob, async=True)

		return self.__hl_command(account, on_success, async)

	def set_options(self, secret, account, async=None, **kwargs):
		""" Sets internal account options. """

		if not account:
			account = address.account_from_seed(secret)

		def on_success(res):
			seq, fee = res
			tx_json = transaction.account_set(
				account,
				seq,
				fee,
				**kwargs
			)
			tx_blob = local.sign(tx_json, secret)
			return self.submit_transaction(tx_blob, async=True)

		return self.__hl_command(account, on_success, async)

	def set_regular_key(self, secret, account, regular_key, async=None):
		""" Sets the regular key for an account. """

		if not account:
			account = address.account_from_seed(secret)

		def on_success(res):
			seq, fee = res
			tx_json = transaction.set_regular_key(
				account,
				regular_key,
				seq,
				fee
			)
			tx_blob = local.sign(tx_json, secret)
			return self.submit_transaction(tx_blob, async=True)

		return self.__hl_command(account, on_success, async)

	def set_trust(self, secret, account, amount, async=None, **kwargs):
		""" Creates a trust line, or modifies an existing one. """

		if not account:
			account = address.account_from_seed(secret)

		def on_success(res):
			seq, fee = res
			tx_json = transaction.trust_set(
				account,
				amount,
				seq,
				fee,
				**kwargs
			)
			tx_blob = local.sign(tx_json, secret)
			return self.submit_transaction(tx_blob, async=True)

		return self.__hl_command(account, on_success, async)
