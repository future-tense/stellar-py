
import unittest
from mock import MagicMock as Mock

import stellar


class DummyPromise(object):

	def __init__(self):
		pass

	def then(self, ok, not_ok):
		self.success = ok
		self.failure = not_ok
		return self

	def resolve(self, res):
		if hasattr(self, 'success'):
			self.callback = self.success
		self.value = res

	def reject(self, err):
		if hasattr(self, 'failure'):
			self.callback = self.failure
		self.value = err

	def get(self):
		if hasattr(self, 'callback'):
			return self.callback(self.value)
		else:
			return self.value


class RemotePromiseTest(unittest.TestCase):

	def setUp(self):
		stellar.remote.Server = Mock
		self.remote = stellar.Remote(None)
		self.server = self.remote.server

	def test_promise_ok(self):
		self.server.request.return_value = DummyPromise()
		p = self.remote.get_account_currencies('account', async=True)
		p.resolve({'result':'ok'})
		self.assertEqual(p.get(), 'ok')

	def test_promise_not_ok(self):
		self.server.request.return_value = DummyPromise()
		p = self.remote.get_account_currencies('account', async=True)
		p.reject("failure")
		self.assertRaises(Exception, p.get)

	def test_get_fee(self):
		self.server.fee_promise = DummyPromise()
		p = self.remote.get_fee(async=True)
		p.resolve(10)
		self.assertEqual(p.get(), 10)


class RemoteParamTest(unittest.TestCase):

	def setUp(self):
		stellar.remote.Server = Mock
		self.remote = stellar.Remote(None)
		self.server = self.remote.server

	def test_cancel(self):
		res = self.remote.cancel("promise")
		self.server.cancel.assert_called_with(
			"promise"
		)

	def test_add_callback(self):

		self.remote.add_callback("tx_type", "callback")
		self.server.add_callback.assert_called_with(
			"tx_type",
			"callback"
		)

	def test_account_currencies_params(self):
		self.remote.get_account_currencies('account')
		self.server.request.assert_called_with(
			'account_currencies',
			account='account'
		)

	def test_account_info_params(self):
		self.remote.get_account_info('account')
		self.server.request.assert_called_with(
			'account_info',
			account='account'
		)

	def test_account_lines_params(self):
		self.remote.get_account_lines('account')
		self.server.request.assert_called_with(
			'account_lines',
			account='account'
		)

	def test_account_offers_params(self):
		self.remote.get_account_offers('account')
		self.server.request.assert_called_with(
			'account_offers',
			account='account'
		)

	def test_account_tx_params(self):
		self.remote.get_account_tx('account')
		self.server.request.assert_called_with(
			'account_tx',
			account='account'
		)

	def test_book_offers_params(self):
		self.remote.get_book_offers('taker_gets', 'taker_pays')
		self.server.request.assert_called_with(
			'book_offers',
			taker_gets='taker_gets',
			taker_pays='taker_pays',
		)

	def test_create_find_path(self):
		self.remote.create_find_path('source', 'dest', 'dest_amount')
		self.server.request.assert_called_with(
			'find_path',
			subcommand='create',
			source_account='source',
			destination_account='dest',
			destination_amount='dest_amount'
		)

	def test_close_find_path(self):
		self.remote.close_find_path()
		self.server.request.assert_called_with(
			'find_path',
			subcommand='close'
		)

	def test_ledger_params(self):
		self.remote.get_ledger(ledger_index='index')
		self.server.request.assert_called_with(
			'ledger',
			ledger_index='index'
		)

	def test_static_path_params(self):
		self.remote.get_static_path(
			'source',
			'dest',
			'dest_amount'
		)
		self.server.request.assert_called_with(
			'static_path_find',
			source_account='source',
			destination_account='dest',
			destination_amount='dest_amount'
		)

	def test_transaction_entry_params(self):
		self.remote.get_transaction_entry('hash', 'index')
		self.server.request.assert_called_with(
			'transaction_entry',
			tx_hash='hash',
			ledger_index='index'
		)

	def test_tx_params(self):
		self.remote.get_tx('tx')
		self.server.request.assert_called_with(
			'tx',
			transaction='tx'
		)

	def test_tx_history_params(self):
		self.remote.get_tx_history('start')
		self.server.request.assert_called_with(
			'tx_history',
			start='start'
		)

	def test_submit_params(self):
		self.remote.submit_transaction('blob')
		self.server.request.assert_called_with(
			'submit',
			tx_blob='blob'
		)

	def test_subscribe_params(self):
		self.remote.subscribe(streams=['stream1', 'stream2'])
		self.server.subscribe.assert_called_with(
			streams=['stream1', 'stream2']
		)

	def test_unsubscribe_params(self):
		self.remote.unsubscribe(streams=['stream1', 'stream2'])
		self.server.unsubscribe.assert_called_with(
			streams=['stream1', 'stream2']
		)
