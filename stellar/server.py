
import websocket
from fee import Fee

import thread
import simplejson as json
import threading

from aplus import Promise

#-------------------------------------------------------------------------------


def _handle_error(self, msg_json):

	tid = msg_json['id']
	if tid in self.requests:

		if 'error_message' in msg_json:
			error_msg = msg_json['error_message']
		else:
			error_msg = msg_json['error']

		request = self.requests[tid]
		promise = request['promise']
		command = request['command']
		del self.requests[tid]
		del self.promises[command]

		promise.reject(Exception(error_msg))

		if msg_json['error'] == 'noNetwork':
			return True
		else:
			return False


def _handle_find_path(self, msg_json):
	self.path_callback(msg_json)
	return True


def _handle_ledger_closed(self, msg_json):

	self.fee.set_fee_scale(msg_json)
	p = Promise()
	p.fulfill(self.fee.calculate_fee())
	self.fee_promise = p
	return True


# These commands always return success, no matter if the stellard
# is synchronized or not, so don't set status to synced when one
# of these occur.
_skiplist = {'ping', 'subscribe', 'unsubscribe'}


def _handle_response(self, msg_json):
	""" Handle messages that arrive as a direct response to a sent command """

	tid = msg_json['id']
	if tid in self.requests:
		request = self.requests[tid]
		promise = request['promise']
		command_key = request['command']

		command_dict = json.loads(command_key)
		command = command_dict['command']

		del self.requests[tid]
		del self.promises[command_key]

		promise.fulfill(msg_json)
		return command not in _skiplist

	else:
		return True


def _handle_server_status(self, msg_json):

	self.fee.set_load_scale(msg_json)
	p = Promise()
	p.fulfill(self.fee.calculate_fee())
	self.fee_promise = p
	return True


def _handle_transaction(self, msg_json):

	if msg_json['status'] != 'closed':
		return True

	if msg_json['engine_result_code'] != 0:
		return True

	tx_type = msg_json['transaction']['TransactionType']
	if tx_type in self.tx_callbacks:
		for callback in self.tx_callbacks[tx_type]:
			callback(msg_json)

	return True

_msg_handlers = {
	'find_path':	_handle_find_path,			# stellar
	'path_find':	_handle_find_path,			# ripple
	'ledgerClosed':	_handle_ledger_closed,
	'response':		_handle_response,
	'serverStatus':	_handle_server_status,
	'transaction':	_handle_transaction,
}


def _on_message(self, message):

	self.event.set()
	msg_json = json.loads(message)

	res = False
	if 'error' in msg_json:
		res = _handle_error(self, msg_json)
		status = False

	else:
		msg_type = msg_json['type']
		if msg_type in _msg_handlers:
			res = _msg_handlers[msg_type](self, msg_json)
			status = True
	#	else:
	#		print msg_type

	if res:
		self._set_sync_status(status)


def _on_error(self, error):
#	print error
	pass


def _on_close(self):
	print "websocket closed"
#	pass


def _on_open(self):
	self.is_open = True
	for tx in self.queue:
		self.send(tx)


class Server(websocket.WebSocketApp):

	def __init__(self, url, callback):
		super(Server, self).__init__(
			url,
			on_open		= _on_open,
			on_message	= _on_message,
			on_error	= _on_error,
			on_close	= _on_close,
		)

		self.fee = Fee()
		self.queue = []
		self.is_open = False

		self.requests = {}
		self.promises = {}
		self.last_id = -1

		self.set_path_callback(None)
		self.set_sync_callback(None)
		self.sync_flag = None

		self.tx_callbacks = {
			'AccountMerge':		[],
			'AccountSet':		[],
			'OfferCancel':		[],
			'OfferCreate':		[],
			'Payment': 			[],
			'SetRegularKey':	[],
			'TrustSet':			[]
		}

		self.__clear_subscriptions()
		self.subscribe_fee()

		self.event = threading.Event()
		self.event.clear()

	def set_path_callback(self, callback):
		self.path_callback = callback if callback else lambda x: None

	def set_sync_callback(self, callback):
		self.sync_callback = callback if callback else lambda x: None

	def _set_sync_status(self, flag):

		if flag != self.sync_flag:
			self.sync_flag = flag
			self.sync_callback(flag)

	def __get_id(self):
		self.last_id +=1
		return self.last_id

	def cancel(self, promise):

		for tid, req in self.requests.items():
			if req['promise'] == promise:
				command_key = req['command']
				del self.requests[tid]
				del self.promises[command_key]

	def __send_request(self, command_key, **kwargs):
		tid = self.__get_id()
		kwargs['id'] = tid
		js = json.dumps(kwargs)

		if self.is_open:
			self.send(js)
		else:
			self.queue.append(js)

		p = Promise()
		request = {
			'command':	command_key,
			'promise':	p
		}

		self.requests[tid] = request
		self.promises[command_key] = p
		return p

	def request(self, command, **kwargs):

		kwargs['command'] = command
		command_key = json.dumps(kwargs, sort_keys=True)
		if command_key not in self.promises:
			return self.__send_request(command_key, **kwargs)
		else:
			return self.promises[command_key]

	def run(self):

		def thread_target():

			while True:
				self.__start_ping_thread()
				self.run_forever()
				self.__stop_ping_thread()
				self.__resubscribe()

		thread.start_new_thread(thread_target, ())

	#
	#	fees
	#

	def subscribe_fee(self):
		""" Start subscribing to network fee updates """
		p = self.subscribe(streams=['ledger', 'server'])\
			.then(self.fee.set_initial_fee)
		self.fee_promise = p

	#
	#	subscription management
	#

	def add_callback(self, tx_type, callback):
		self.tx_callbacks[tx_type].append(callback)

	def __clear_subscriptions(self):

		self.subscriptions = {
			'streams':		[],
			'accounts':		[],
			'accounts_rt':	[],
			'books':		[]
		}

	def __resubscribe(self):

		kwargs = {}
		for key, value in self.subscriptions.iteritems():
			if value:
				kwargs[key] = [
					json.loads(item)
					for item in value
				]

		self.request('subscribe', **kwargs)

	def subscribe(self, **kwargs):

		for key, value in kwargs.iteritems():

			value = [
				json.dumps(item, sort_keys=True)
				for item in value
			]

			t = self.subscriptions[key]
			t = list(set(t).union(value))
			self.subscriptions[key] = t

		return self.request('subscribe', **kwargs)

	def unsubscribe(self, **kwargs):

		for key, value in kwargs.iteritems():

			value = [
				json.dumps(item, sort_keys=True)
				for item in value
			]

			t = self.subscriptions[key]
			t = list(set(t).difference(value))
			self.subscriptions[key] = t

		return self.request('unsubscribe', **kwargs)

	#
	#	ping thread management
	#

	def __ping_thread_target(self):
		while not self.end_ping_thread:
			if not self.event.wait(30):
				self.request('ping')
			self.event.clear()

	def __start_ping_thread(self):
		self.event = threading.Event()
		self.end_ping_thread = False
		self.ping_thread = threading.Thread(target=self.__ping_thread_target)
		self.ping_thread.setDaemon(True)
		self.ping_thread.start()

	def __stop_ping_thread(self):
		self.end_ping_thread = True
		self.event.set()
		self.ping_thread.join()
