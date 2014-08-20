#!/usr/bin/python

import stellar
import argparse


def parse_amount(m):

	if not '.' in m:
		m = int(m) * 1000000
	else:
		i, f = m.split('.')
		m = int(i + f)
		m *= 1000000
		m /= 10 ** len(f)
	return m


def send(secret, account_id, destination, amount):

	if not account_id:
		seed	   = stellar.Seed.from_human(secret)
		account_id = stellar.AccountID.from_seed(seed).to_human()

	amount = parse_amount(amount)

	tx_json = {
		'TransactionType': 	'Payment',
		'Account': 			account_id,
		'Amount': 			amount,
	}

	d = destination.split("?dt=")
	if len(d) == 2:
		tx_json['DestinationTag'] = int(d[1])
	tx_json['Destination'] = d[0]

	tx_blob = stellar.sign_transaction(secret, tx_json)
	stellar.submit_transaction(tx_blob)


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
	send(args.secret, args.source, args.destination, args.amount)


if __name__ == '__main__':
	main()
