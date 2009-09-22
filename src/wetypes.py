class WeTypes:
	@staticmethod
	def int_to_bytes(num):
		#print "i2ba", num, hex(num)
		s = hex(num)[2:]
		if s[-1] == 'L': s = s[:-1]
		#print s, s[0:1]
		if len(s) % 2 != 0:
			s = '0'+s
		a = [int(s[2*i:2*i+2],16) for i in xrange(len(s)/2)]
		#print a
		return a

	@staticmethod
	def hex_to_bytes(s):
		if s[:2] == '0x':
			s = s[2:]
		if s[-1] == 'L': s = s[:-1]
		if len(s) % 2 != 0:
			s = '0'+s
		a = [int(s[2*i:2*i+2], 16) for i in xrange(len(s)/2)]
		return a

	@staticmethod
	def bytes_to_hex(a):
		#print "BA2HS: "+str(a)
		t = [hex(n)[2:] for n in a]
		for i in xrange(len(t)):
			if len(t[i]) == 1:
				t[i] = '0'+t[i]
		return "".join(t)

	@staticmethod
	def bytes_to_int(a):
		return int(WeTypes.bytes_to_hex(a), 16)

	@staticmethod
	def bytes_to_cbytes(a):
		return array.array('B', a)

	@staticmethod
	def bytes_to_string(a):
		return "".join( (chr(x) for x in a) )

	@staticmethod
	def string_to_bytes(a):
		return [ord(c) for c in a]

	@staticmethod
	def make_random_bytes(minlen, maxlen=None):
		random.seed()
		if maxlen:
			n = random.randint(minlen, maxlen)
		else:
			n = minlen
		randBytes = [random.randint(0, 255) for x in xrange(n)]
		#print "x", randBytes
		#r = raw_input()
		return randBytes

	@staticmethod
	def zero_pad(a, n):
		pad_len = n-len(a)
		if pad_len > 0:
			return [0]*pad_len + a
		else:
			return a
