from common import *

from django.db import models

class UserData(models.Model):
	usercode = models.CharField(max_length=usercode_len)
	apikey = models.CharField(max_length=apikey_len)
	nickname = models.CharField(max_length=512)
	email = models.EmailField()
	pastes_hidden_by_default = models.BooleanField(default=False)
	friends_hidden_by_default = models.BooleanField(default=False)
	
	def get_usercode(self):
		return self.usercode
	def get_absolute_url(self):
		return '/profile/'+self.usercode
	
	@staticmethod
	def get_by_code(code):
		udatas = UserData.objects.filter(usercode=code)
		if udatas.count() != 1:
			return None
		else:
			return udatas.fetch(1)[0]	

	@staticmethod
	def get_by_codes(codes):
		return UserData.objects.filter(usercode__in=codes)
			
	@staticmethod
	def get_apikey_by_code(code):
		udata = UserData.filter_by_code(code)
		if not (udata is None):
			return udata.apikey
		else:
			return None
	
	@staticmethod
	def check_apikey(code, key):
		return (key == UserData.filter_apikey_by_code(key))