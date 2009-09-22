from common import *

from django.db import models

class Friend(models.Model):
	my_code = models.CharField(max_length=usercode_len)
	their_code = models.CharField(max_length=usercode_len)
	date_friended = models.DateTimeField(auto_now_add=True)
	
	def get_usercode(self):
		return self.their_code
	def get_absolute_url(self):
		return '/profile/'+self.their_code
	
	@staticmethod
	def make_friends(code1, code2):
		Friend.create(my_code=code1, their_code=code2).save()
	
	@staticmethod
	def unmake_friends(code1, code2):
		friend = Friend.objects.filter(code1=code1, code2=code2)
		db.delete(friend)

	@staticmethod
	def get_who_i_follow(code):
		return Friend.objects.filter(my_code=code)
			
	@staticmethod
	def get_who_follows_user(code):
		return Friend.objects.filter(their_code=code)

	@staticmethod
	def already_present(code1, code2):
		return Friend.objects.filter(my_code=code1, their_code=code2).count() > 0
