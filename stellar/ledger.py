
import config
import urllib2
import simplejson as json

#-------------------------------------------------------------------------------


def get_account_info(account_id):

	url = config.stellard_url
	data = '{"method":"account_info","params":[{"account":"%s"}]}' % account_id

	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)
	res = response.read()

	js = json.loads(res)
	return js['result']['account_data']


def get_sequence_number(account_id):
	ai = get_account_info(account_id)
	return ai['Sequence']

#-------------------------------------------------------------------------------
