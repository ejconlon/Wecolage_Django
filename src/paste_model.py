from common import *

import random, datetime

from codes_model import Pastecode

from django.db import models

class Paste(models.Model):
	pastecode = models.CharField(max_length=pastecode_len, primary_key=True)
	usercode = models.CharField(max_length=usercode_len)
	name = models.CharField(max_length=512)
	description = models.TextField()
	content = models.TextField()
	parsed_content = models.TextField()
	parent_diff = models.TextField()
	parsed_parent_diff = models.TextField()
	format = models.CharField(max_length=128)
	date_created = models.DateTimeField(auto_now_add=True)
	password_hash = models.CharField(max_length=256)
	hidden = models.BooleanField(default=False)
	parent_code = models.CharField(max_length=pastecode_len)
	ancestor_code = models.CharField(max_length=pastecode_len)
	marked_for_deletion = models.BooleanField(default=False)
	
	def check_password(self, password):
		if password is None or len(password)==0:
			return (self.password_hash is None)
		else:
			test_hash = sha1(self.pastecode + password + self.pastecode)
			return (self.password_hash == test_hash)
	
	def save_new(self, password=None):
		self.pastecode = Pastecode().new_code()
		if not (password is None) and len(password) > 0:
			self.password_hash = sha1(pastecode + password + pastecode)
		self.save()

	def start_fork(self, usercode=None):
		paste = Paste()
		paste.usercode = usercode
		paste.name = self.name
		paste.content = self.content
		paste.parsed_content = self.parsed_content
		paste.format = self.format
		paste.date_created = datetime.datetime.now()
		paste.parent_code = self.pastecode
		if self.ancestor_code is None:
			paste.ancestor_code = self.pastecode
		else:
			paste.ancestor_code = self.ancestor_code
		return paste
	
	def get_usercode(self):
		return self.usercode
	def get_absolute_url(self):
		return '/paste/'+self.pastecode

	@staticmethod
	def get_by_code(pastecode):
		pastes = Paste.objects.filter(pastecode=pastecode)
		if pastes.count() != 1:
			return None
		else:
			return pastes.fetch(1)[0]
			
	@staticmethod
	def get_all_by_usercode(usercode):
		return Paste.objects.filter(usercode=usercode).order_by('date_created')
		
	@staticmethod
	def get_public_by_usercode(usercode):
			return Paste.objects.filter(usercode=usercode, hidden=False).order_by('date_created')
		
	@staticmethod	
	def get_most_recent_public():
		return Paste.objects.filter(hidden=False).order_by('date_created')
