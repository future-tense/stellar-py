#!/usr/bin/python

import stellar
import sys


def main():

	if len(sys.argv) > 1:
		account, secret = stellar.generate_keypair(password=sys.argv[1])
	else:
		account, secret = stellar.generate_keypair()

	print 'Account ID: ', account
	print 'Secret key: ', secret

if __name__ == '__main__':
	main()
