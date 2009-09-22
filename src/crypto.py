from wetypes import *
from Crypto.Cipher import AES

class WeCrypto:
	# makes somewhere between minlen and maxlen (inclusive) random bytes
	class aes_counter:
		def __init__(self, start = 0):
			self.count = start
		def __call__(self):
			c = WeTypes.int_to_bytes(self.count)
			self.count += 1
			return WeTypes.bytes_to_string(WeTypes.zero_pad(c, 16))

	# AES128-CTR - handles arbitrary length data, key must be 128 bits
	# it is its own inverse (XOR)
	@staticmethod
	def aes_ctr_crypt(key, data_orig, ctr_val):
		data = [x for x in data_orig]
		AESr = AES.new(WeTypes.bytes_to_cbytes(key), AES.MODE_CTR, counter=OtrCrypt.aes_counter(ctr_val))
		# need to fill to a multiple of 16; since it is in 
		# counter mode, we can just ignore the end of the encrypted output
		fill_len = (16 - (len(data) % 16)) % 16
		data.extend([0]*fill_len)
		# do the encryption
		enc_str = AESr.encrypt(WeTypes.bytes_to_cbytes(data))
		return WeTypes.string_to_bytes(enc_str[:-fill_len])

	@staticmethod
	def aes_zero_ctr_crypt(key, data_orig):
		return OtrCrypt.aes_ctr_crypt(key, data_orig, ctr_val=0)