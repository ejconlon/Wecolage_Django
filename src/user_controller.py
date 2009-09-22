from common import *

import cgi, sessions

from paste_model import Paste
from userdata_model import UserData
from friend_model import Friend
from friendrequest_model import FriendRequest

from google.appengine.ext.webapp import template

class Profile(sessions.PersistentRequestHandler):
	def get(self, usercode=None):
		self.init_session()
		if self.do_redirect(): return
		
		if usercode is None:
			usercode = self.get_key('usercode')
			if usercode is None:
				self.redirect('/login')
				return
			else:
				self.redirect('/profile/'+usercode)
				return
		elif usercode[0] == '/':
			usercode = usercode[1:]
		
		my_usercode = self.get_key('usercode')
		your_profile = (usercode == self.get_key('usercode'))

		if not your_profile:
			userdata = UserData.get_by_code(usercode)
			if not (my_usercode is None):
				are_friends = Friend.already_present(my_usercode, usercode)
				if not are_friends:
					
					if not userdata.friends_hidden_by_default:
						list_link = '/friends/'+usercode
					else:
						list_link = None
					
					if FriendRequest.already_present(my_usercode, usercode):
						#print "AWAITING REPLY"
						awaiting_reply = True
						approve_link = reject_link = None
						friend_link = unfriend_link = None
					elif FriendRequest.already_present(usercode, my_usercode):
						#print "APPROVE REJECT"
						awaiting_reply = False
						approve_link = '/friends/approve/'+usercode
						reject_link = '/friends/reject/'+usercode
						friend_link = unfriend_link = None
					else:
						friend_link = '/friends/request/'+usercode
						unfriend_link = None
						approve_link = reject_link = awaiting_reply = None
				else:
					friend_link = None
					unfriend_link = '/friends/remove/'+usercode
					list_link = '/friends/'+usercode
					approve_link = reject_link = awaiting_reply = None
			else:
				are_friends = False
				approve_link = reject_link = awaiting_reply = None
				friend_link = unfriend_link = list_link = None
			pastes = Paste.get_public_by_usercode(usercode)
			self.template_values.update({ 
				'prof_nickname': userdata.nickname,
				'prof_usercode': usercode,
				'profile_link': '/profile/'+usercode,
				'pastes': pastes,
				'num_pastes': pastes.count(),
				'are_friends': are_friends,
				'your_profile': your_profile,
				'friend_link': friend_link,
				'unfriend_link': unfriend_link,
				'list_link': list_link,
				'approve_link': approve_link,
				'reject_link': reject_link,
				'awaiting_reply': awaiting_reply
			})
		else:
			pastes = Paste.get_all_by_usercode(usercode)	
			self.template_values.update({	
				'prof_nickname': self.session['nickname'],
				'prof_usercode': usercode, 
				'profile_link': '/profile/'+usercode,
				'pastes': pastes,
				'num_pastes': pastes.count(),
				'your_profile': your_profile
			})
			
		path = get_template_path('profile.html')
		self.response.out.write(template.render(path, self.template_values, debug=True)) 

class Settings(sessions.PersistentRequestHandler):
	  def get(self):
		self.init_session()
		if self.do_redirect(): return

		if 'usercode' not in self.session:
			#print self.session
			self.redirect('/login')
			return
		
		self.template_values.update({
			'apikey': UserData.get_apikey_by_code(self.session['usercode'])
		})
		
		path = get_template_path('settings.html')
		self.response.out.write(template.render(path, self.template_values, debug=True))