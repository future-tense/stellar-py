
def to_hex(s):
	return s.encode('hex').upper()


def bytes_to_int(v, base=256):

	value = 0
	for byte in v:
		value *= base
		value += ord(byte)

	return value


def int_to_bytes(value, base=256, size=None):

	result = ''
	while value > 0:
		value, mod = divmod(value, base)
		result += chr(mod)

	if size:
		size -= len(result)
		for n in xrange(size):
			result += '\0'

	return result[::-1]
