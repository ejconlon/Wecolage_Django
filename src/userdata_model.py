from common import *

from django.db import model

class UserData(model.Model):
	usercode = model.CharField()
	apikey = model.CharField()
	nickname = model.CharField()
	email = model.EmailField()
	pastes_hidden_by_default = model.BooleanField(default=False)
	friends_hidden_by_default = model.BooleanField(default=False)
	
	def get_usercode(self):
		return self.usercode
	def get_absolute_url(self):
		return '/profile/'+self.usercode
	
	@staticmethod
	def get_by_code(code):
		udatas = UserData.objects.get(usercode=code)
		if udatas.count() != 1:
			return None
		else:
			return udatas.fetch(1)[0]	

	@staticmethod
	def get_by_codes(codes):
		return UserData.objects.get(usercode__in=codes)
			
	@staticmethod
	def get_apikey_by_code(code):
		udata = UserData.get_by_code(code)
		if not (udata is None):
			return udata.apikey
		else:
			return None
	
	@staticmethod
	def check_apikey(code, key):
		return (key == UserData.get_apikey_by_code(key))