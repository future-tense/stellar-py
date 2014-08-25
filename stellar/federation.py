import urllib2
import simplejson as json

import cPickle as pickle
import os.path

#-------------------------------------------------------------------------------

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')]
urllib2.install_opener(opener)

#-------------------------------------------------------------------------------


class FederationCache(object):

	def __init__(self):

		self.forward_url = {}
		self.reverse_url = {}
		self.account_id  = {}
		self.username    = {}
		self.initialized = False

	def _init(self):
		self.initialized = True

	def _update(self):
		pass

	def get_account(self, name):

		if not self.initialized:
			self._init()

		if name in self.account_id:
			return self.account_id[name]

		name, domain = name.split('@')
		res = self.__get_federated_account(name, domain)
		if res:
			self.account_id['%s@%s' % (name, domain)] = res
			self._update()

		return res

	def __get_federated_account(self, name, domain):

		url = self.__get_forward_url(domain)
		query = '?destination=%s&domain=%s&type=federation&user=%s' % (name, domain, name)

		req = urllib2.Request(url + query)
		response = urllib2.urlopen(req)
		res = response.read()
		js = json.loads(res)

		if 'federation_json' in js:
			res = js['federation_json']['destination_address']
			return res
		else:
			return None

	def __get_forward_url(self, domain):

		if domain in self.forward_url:
			return self.forward_url[domain]
		else:
			self._get_federation_settings(domain)
			if domain in self.forward_url:
				return self.forward_url[domain]
			else:
				return None

	def _get_federation_settings(self, domain):

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
				self.forward_url[domain] = s[1]
				s = s[2:]
			elif s[0] == '[reverse_federation_url]':
				self.reverse_url[domain] = s[1]
				s = s[2:]
			else:
				s = s[1:]

#-------------------------------------------------------------------------------


class FileFederationCache(FederationCache):

	def __init__(self, filename):
		super(FileFederationCache, self).__init__()
		self.filename = filename

	def _init(self):

		if os.path.exists(self.filename):
			f = open(self.filename, 'rb')
			self.forward_url = pickle.load(f)
			self.reverse_url = pickle.load(f)
			self.account_id  = pickle.load(f)
			self.username    = pickle.load(f)
			f.close()

		self.initialized = True

	def _update(self):
		f = open(self.filename, 'wb')
		pickle.dump(self.forward_url, f, -1)
		pickle.dump(self.reverse_url, f, -1)
		pickle.dump(self.account_id, f, -1)
		pickle.dump(self.username, f, -1)
		f.close()

#-------------------------------------------------------------------------------

cache = FederationCache()

#-------------------------------------------------------------------------------


def get_account(name):

	name = name.lower()
	if not '@' in name:
		name += '@stellar.org'

	return cache.get_account(name)

#-------------------------------------------------------------------------------


#def get_username(account_id):
#
#	url = reverse_url['stellar.org']
#	query = "?destination_address=%s&domain=stellar.org" % (account_id)
#
#	req = urllib2.Request(url + query)
#	response = urllib2.urlopen(req)
#	res = response.read()
#	js = json.loads(res)
#
#	if 'federation_json' in js:
#		return js['federation_json']['destination']
#	else:
#		return None

#-------------------------------------------------------------------------------

