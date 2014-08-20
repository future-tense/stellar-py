
import stellar
import sys


def main():

	if len(sys.argv) > 1:
		seed = stellar.get_seed_generic(sys.argv[1])
		seed = stellar.Seed(seed)
	else:
		seed = stellar.Seed.random()

	print 'Account ID: ', stellar.AccountID.from_seed(seed).to_human()
	print 'Seed:       ', seed.to_human()
	print 'Public Key: ', stellar.Public.from_seed(seed).to_human()

if __name__ == '__main__':
	main()
