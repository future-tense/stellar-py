
def to_hex(s):
	return ''.join(x.encode('hex') for x in s).upper()


def int_to_bytes(value, size):

	result = ''
	while value >= 256:
		value, mod = divmod(value, 256)
		result += chr(mod)
		size -= 1
	result += chr(value)

	for n in xrange(size-1):
		result += '\0'

	return result[::-1]
