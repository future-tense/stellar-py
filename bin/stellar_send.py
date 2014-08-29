#!/usr/bin/python

import stellar
import argparse


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

	res, msg = stellar.send_payment(
		args.secret, args.source, args.destination, args.amount)

	print msg

#-------------------------------------------------------------------------------


if __name__ == '__main__':
	main()
