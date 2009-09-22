from common import *

import random, datetime

from codes_model import Pastecode

from django.db import model

class Paste(model.Model):
	pastecode = model.CharField()
	usercode = model.CharField()
	name = model.CharField()
	description = model.TextField()
	content = model.TextField()
	parsed_content = model.TextField()
	parent_diff = model.TextField()
	parsed_parent_diff = model.TextField()
	format = model.CharField()
	date_created = model.DateTimeField(auto_now_add=True)
	password_hash = model.CharField()
	hidden = model.BooleanField(default=False)
	parent_code = model.CharField()
	ancestor_code = model.CharField()
	marked_for_deletion = model.BooleanField(default=False)
	
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
		pastes = Paste.objects.get(pastecode=pastecode)
		if pastes.count() != 1:
			return None
		else:
			return pastes.fetch(1)[0]
			
	@staticmethod
	def get_all_by_usercode(usercode):
		return Paste.objects.get(usercode=usercode).order_by('date_created')
		
	@staticmethod
	def get_public_by_usercode(usercode):
			return Paste.objects.get(usercode=usercode, hidden=False).order_by('date_created')
		
	@staticmethod	
	def get_most_recent_public():
		return Paste.objects.get(hidden=False).order_by('date_created')
