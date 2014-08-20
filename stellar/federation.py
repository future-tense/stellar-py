
#	https://stellar.stellar.org/stellar.txt


import urllib2
import simplejson as json

#-------------------------------------------------------------------------------

FEDERATION_URL 			= "https://api.stellar.org/federation"
REVERSE_FEDERATION_URL	= "https://api.stellar.org/reverseFederation"

#-------------------------------------------------------------------------------

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')]
urllib2.install_opener(opener)

#-------------------------------------------------------------------------------


def get_accountid_from_username(name):

	url = FEDERATION_URL
	query = "?destination=%s&domain=stellar.org&type=federation&user=%s" % (name, name)

	req = urllib2.Request(url + query)
	response = urllib2.urlopen(req)
	res = response.read()
	js = json.loads(res)

	if 'federation_json' in js:
		return js['federation_json']['destination_address']
	else:
		return None

#-------------------------------------------------------------------------------


def get_username_from_accountid(account_id):

	url = REVERSE_FEDERATION_URL
	query = "?destination_address=%s&domain=stellar.org" % (account_id)

	req = urllib2.Request(url + query)
	response = urllib2.urlopen(req)
	res = response.read()
	js = json.loads(res)

	if 'federation_json' in js:
		return js['federation_json']['destination']
	else:
		return None

#-------------------------------------------------------------------------------
