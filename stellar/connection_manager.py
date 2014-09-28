
import websocket
import thread
import simplejson as json
import threading

from aplus import Promise

#-------------------------------------------------------------------------------


def handle_error(self, msg_json):

	tid = msg_json['id']
	if tid in self.requests:
		error_msg = msg_json['error_message']
		request = self.requests[tid]
		promise = request['promise']
		command = request['command']
		del self.requests[tid]
		del self.promises[command]
		promise.reject(Exception(error_msg))

		if msg_json['error'] == 'noNetwork':
			self.set_synced(False)
			print "out of sync", command
		else:
			print command

command_blacklist = {'ping', 'subscribe', 'unsubscribe'}
"""
These commands always return success, no matter if the stellard
is synchronized or not, so don't set status to synced when one
of these occur.
"""


def handle_find_path(self, msg_json):
	pass


def handle_ledger_closed(self, msg_json):

	self.set_synced(True)
	set_fee_scale(msg_json)


def handle_response(self, msg_json):

	tid = msg_json['id']
	if tid in self.requests:
		request = self.requests[tid]
		promise = request['promise']
		command_key = request['command']

		command_dict = json.loads(command_key)
		command = command_dict['command']
		if not command in command_blacklist:
			self.set_synced(True)

		del self.requests[tid]
		del self.promises[command_key]
		print request['command']

		promise.fulfill(msg_json)


def handle_server_status(self, msg_json):

	self.set_synced(True)
	set_load_scale(msg_json)


def handle_transaction(self, msg_json):

	self.set_synced(True)
	if msg_json['status'] != 'closed':
		return

	if msg_json['engine_result_code'] != 0:
		return

	tx_type = msg_json['transaction']['TransactionType'].lower()
	if tx_type in self.tx_callbacks:
		for callback in self.tx_callbacks[tx_type]:
			callback(msg_json)

#-------------------------------------------------------------------------------

msg_handlers = {
	'find_path':	handle_find_path,
	'ledgerClosed':	handle_ledger_closed,
	'response':		handle_response,
	'serverStatus':	handle_server_status,
	'transaction':	handle_transaction,
}

#-------------------------------------------------------------------------------


def on_message(self, message):

	self.event.set()
	msg_json = json.loads(message)

	if 'error' in msg_json:
		handle_error(self, msg_json)

	else:
		msg_type = msg_json['type']
		if msg_type in msg_handlers:
			msg_handlers[msg_type](self, msg_json)


def on_error(self, error):
	print error


def on_close(self):
	print "websocket closed"


def on_open(self):
	self.is_open = True
	for tx in self.queue:
		self.send(tx)

#-------------------------------------------------------------------------------


class ConnectionManager(websocket.WebSocketApp):

	def __init__(self, url):
		super(ConnectionManager, self).__init__(url,
			on_open	   = on_open,
			on_message = on_message,
			on_error   = on_error,
			on_close   = on_close
		)
		self.queue = []
		self.is_open = False

		self.requests = {}
		self.promises = {}
		self.last_id = -1
		self.synced = None

		self.sync_callback = None
		self.tx_callbacks = {
			'trustset': [],
			'payment':	[],
		}

		self.event = threading.Event()
		self.event.clear()

	def add_callback(self, tx_type, callback):
		self.tx_callbacks[tx_type].append(callback)

	def set_sync_callback(self, callback):
		self.sync_callback = callback

	def set_synced(self, flag):

		if flag != self.synced:
			self.synced = flag
			if self.sync_callback:
				self.sync_callback(flag)

	def get_id(self):
		self.last_id +=1
		return self.last_id

	def request(self, command, **kwargs):

		kwargs['command'] = command
		command_key = json.dumps(kwargs, sort_keys=True)

		if command_key in self.promises:
			p = self.promises[command_key]
			print command, "cached"

		else:
			tid = self.get_id()
			kwargs['id'] = tid
			js = json.dumps(kwargs)
			print command, tid

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

	def ping_thread_target(self):
		while not self.end_ping_thread:
			if not self.event.wait(30):
				self.request('ping')
			self.event.clear()

	def start_ping_thread(self):
		self.event = threading.Event()
		self.end_ping_thread = False
		self.ping_thread = threading.Thread(target=self.ping_thread_target)
		self.ping_thread.setDaemon(True)
		self.ping_thread.start()

	def stop_ping_thread(self):
		self.end_ping_thread = True
		self.event.set()
		self.ping_thread.join()

	def run(self):
		self.start_ping_thread()
		self.run_forever()
		self.stop_ping_thread()

#-------------------------------------------------------------------------------


def request(command, **kwargs):
	return cm.request(command, **kwargs)


def subscribe(**kwargs):
	return cm.request('subscribe', **kwargs)


def unsubscribe(**kwargs):
	return cm.request('unsubscribe', **kwargs)


def add_callback(tx_type, callback):
	cm.add_callback(tx_type, callback)


def set_sync_callback(callback):
	cm.set_sync_callback(callback)


def run():
	while True:
		cm.run()

#-------------------------------------------------------------------------------

cm = ConnectionManager("ws://live.stellar.org:9001/")
thread.start_new_thread(run, ())

#-------------------------------------------------------------------------------

fee_structure = {
	'default_fee': 10,
	'fee_cushion': 1.2,
}


def set_fee_scale(tx):
	fee_base  = float(tx['fee_base'])
	fee_ref   = float(tx['fee_ref'])
	fee_scale = fee_base / fee_ref
	fee_structure['fee_scale']  = fee_scale


def set_load_scale(tx):
	load_base	 = float(tx['load_base'])
	load_factor  = float(tx['load_factor'])
	load_scale	 = load_factor / load_base
	fee_structure['load_scale'] = load_scale


def get_fee():
	f = fee_structure
	return int(f['default_fee'] * f['fee_scale'] * f['load_scale'])


def set_initial_fee(tx_json):
	result = tx_json['result']
	set_fee_scale(result)
	set_load_scale(result)

#-------------------------------------------------------------------------------

subscribe(streams=['ledger', 'server']).then(set_initial_fee)
#request('subscribe', streams=['ledger', 'server']).then(set_initial_fee)

#-------------------------------------------------------------------------------
