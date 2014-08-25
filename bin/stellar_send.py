#!/usr/bin/python

import stellar
import argparse

import appdirs
import os


def setup_cache():

	cache_dir = appdirs.user_cache_dir("stellar-py", "Pollen 23")
	if not os.path.exists(cache_dir):
		os.makedirs(cache_dir)

	cache_file = "%s/federation.dat" % cache_dir
	stellar.federation.cache = stellar.FileFederationCache(cache_file)


def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--source',
		help='Source account, if not derived from secret')

	parser.add_argument('destination',
		help='Destination account')

	parser.add_argument('amount',
		help='Amount to send')

	parser.add_argument('secret',
		help='Secret key')

	args = parser.parse_args()

	setup_cache()
	stellar.send_payment(args.secret, args.source, args.destination, args.amount)

#-------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
