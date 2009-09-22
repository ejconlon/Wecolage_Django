from common import *

from django.db import models

class FriendRequest(models.Model):
	my_code = models.CharField(max_length=usercode_len)
	their_code = models.CharField(max_length=usercode_len)
	date_requested = models.DateTimeField(auto_now_add=True)
	
	@staticmethod
	def make_request(code1, code2):
		FriendRequest.create(my_code=code1, their_code=code2).save()
	
	@staticmethod
	def unmake_request(code1, code2):
		request = FriendRequest.objects.filter(code1=code1, code2=code2)
		db.delete(request)

	@staticmethod
	def get_who_user_requested_to_follow(code):
		return FriendRequest.objects.filter(my_code=code)
	
	@staticmethod
	def get_who_requested_to_follow_user(code):
		return FriendRequest.objects.filter(their_code=code)
	
	@staticmethod
	def already_present(code1, code2):
		return FriendRequest.objects.filter(my_code=code1, their_code=code2).count() > 0
	
	@staticmethod
	def get_number_of_requests(code):
		return FriendRequest.filter_who_requested_to_follow_user(code).count()