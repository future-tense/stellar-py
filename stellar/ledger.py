from connection_manager import *

from aplus import Promise


def get_account_info_promise(account_id):

	p = Promise()

	def on_response(js):

		res = js['result']
		if 'account_data' in res:
			ai = res['account_data']
			p.fulfill(ai)
		else:
			error_msg = res['error_message']
			p.reject(Exception(error_msg))

	cm.send_command('account_info', account=account_id).then(on_response)
	return p


def get_sequence_number_promise(account_id):

	def on_account_info(ai):
		return Promise.fulfilled(ai['Sequence'])

	return get_account_info_promise(account_id).then(on_account_info)


def get_account_info(account_id):
	return get_account_info_promise(account_id).get(timeout=10)


def get_sequence_number(account_id):
	return get_sequence_number_promise(account_id).get(timeout=10)

#-------------------------------------------------------------------------------
