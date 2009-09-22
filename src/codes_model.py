from common import *

from django.db import models

class Code(models.Model):
	code = models.CharField(max_length=max_code_len)
	
	def __generate_code(self):
		return "".join((random.choice(self.code_chars) for i in xrange(self.code_len)))
	
	def new_code(self):
		while True:
			code = self.__generate_code()
			present_codes = self.objects.get(code=code)
			if (present_codes.count() == 0):
				break
		self.code = code
		self.put()
		return code
	
	def already_used(self, code):
		return self.objects.get(code=code).count()>0
		
class Pastecode(Code):
	code_len = pastecode_len
	code_chars = [x for x in "012345789abcdefghijklmnopqrstuvwxyz"]
class Usercode(Code):
	code_len = usercode_len
	code_chars = [x for x in "012345789abcdefghijklmnopqrstuvwxyz"]
class Apikey(Code):
	code_len = apikey_len
	code_chars = [x for x in "012345789abcdefghijklmnopqrstuvwxyz"]
