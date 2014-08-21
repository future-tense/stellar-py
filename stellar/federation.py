import urllib2
import simplejson as json

import cPickle as pickle
import os.path

#-------------------------------------------------------------------------------

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')]
urllib2.install_opener(opener)

#-------------------------------------------------------------------------------

forward_url = {}
reverse_url = {}
account_id  = {}
username    = {}

#-------------------------------------------------------------------------------


def get_forward_url(domain):

	if domain in forward_url:
		return forward_url[domain]
	else:
		get_federation_settings(domain)
		if domain in forward_url:
			return forward_url[domain]
		else:
			return None


def get_federation_settings(domain):

	global dirty
	s = None

	prefix = ['stellar.', 'www.', '']
	for p in prefix:

		url = 'https://%s%s/stellar.txt' % (p, domain)
		req = urllib2.Request(url)

		try:
			response = urllib2.urlopen(req)
		except urllib2.URLError:
			pass
		else:
			s = response.read().splitlines()
			break

	while s:
		if s[0] == '[federation_url]':
			forward_url[domain] = s[1]
			dirty = True
			s = s[2:]
		elif s[0] == '[reverse_federation_url]':
			reverse_url[domain] = s[1]
			dirty = True
			s = s[2:]
		else:
			s = s[1:]

#-------------------------------------------------------------------------------


def get_accountid(name):

	name = name.lower()
	if not '@' in name:
		name += '@stellar.org'

	if name in account_id:
		return account_id[name]

	#

	global dirty

	name, domain = name.split('@')

	url = get_forward_url(domain)
	query = '?destination=%s&domain=%s&type=federation&user=%s' % (name, domain, name)

	req = urllib2.Request(url + query)
	response = urllib2.urlopen(req)
	res = response.read()
	js = json.loads(res)

	if 'federation_json' in js:
		res = js['federation_json']['destination_address']
		account_id['%s@%s' % (name, domain)] = res
		dirty = True
	else:
		res = None

	if dirty:
		f = open(filename, 'wb')
		pickle.dump(forward_url, f, -1)
		pickle.dump(reverse_url, f, -1)
		pickle.dump(account_id, f, -1)
		pickle.dump(username, f, -1)
		f.close()
		dirty = False

	return res

#-------------------------------------------------------------------------------


def get_username(account_id):

	url = reverse_url['stellar.org']
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

filename = 'federation.dat'
dirty = False

if os.path.exists(filename):
	f = open(filename, 'rb')
	forward_url = pickle.load(f)
	reverse_url = pickle.load(f)
	account_id  = pickle.load(f)
	username    = pickle.load(f)
	f.close()
else:
	get_federation_settings('stellar.org')

#-------------------------------------------------------------------------------

