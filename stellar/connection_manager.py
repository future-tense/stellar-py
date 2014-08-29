
import websocket
import thread
import simplejson as json
import threading

from aplus import Promise

#-------------------------------------------------------------------------------


def on_message(self, message):

	self.event.set()
	tx_json = json.loads(message)

	if 'error' in tx_json:

		if tx_json['error'] == 'noNetwork':
			self.set_synced(False)

		tid = tx_json['id']
		if tid in self.promises:
			error_msg = tx_json['error_message']
			promise = self.promises[tid]
			del self.promises[tid]
			promise.reject(Exception(error_msg))

	else:
		self.set_synced(True)

		if tx_json['type'] == 'response':
			tid = tx_json['id']
			if tid in self.promises:
				promise = self.promises[tid]
				del self.promises[tid]
				promise.fulfill(tx_json)

		else:
			if self.stream_callback:
				self.stream_callback(tx_json)


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
		self.promises = {}
		self.last_id = -1
		self.synced = None
		self.stream_callback = None
		self.sync_callback = None
		self.event = threading.Event()
		self.event.clear()

	def set_stream_callback(self, callback):
		self.stream_callback = callback

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

	def send_command(self, command, **kwargs):

		tid = self.get_id()
		kwargs['command'] = command
		kwargs['id'] = tid
		js = json.dumps(kwargs)

		if self.is_open:
			self.send(js)
		else:
			self.queue.append(js)

		p = Promise()
		self.promises[tid] = p
		return p

	def ping_thread_target(self):
		while not self.end_ping_thread:
			if not self.event.wait(30):
				self.send_command('ping')
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


def send(command, **kwargs):
	return cm.send_command(command, **kwargs)


def set_stream_callback(callback):
	cm.set_stream_callback(callback)


def run():
	while True:
		cm.run()

#-------------------------------------------------------------------------------

cm = ConnectionManager("ws://live.stellar.org:9001/")
thread.start_new_thread(run, ())

#-------------------------------------------------------------------------------
