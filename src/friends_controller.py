from common import *

import cgi, sessions

from friend_model import Friend
from friendrequest_model import FriendRequest
from userdata_model import UserData

from google.appengine.ext.webapp import template

class ListFriends(sessions.PersistentRequestHandler):
	def get(self, usercode=None):
		self.init_session()
		if self.do_redirect(): return
			
		if usercode is None:
			usercode = self.get_key('usercode')
			if usercode is None: # no session
				self.redirect('/login')
				return
		elif usercode[0] == '/':
			usercode = usercode[1:]
			
		your_friends = (usercode == self.get_key('usercode'))
			
		userdata = UserData.get_by_code(usercode)
		if your_friends:
			friend_requests = FriendRequest.get_who_requested_to_follow_user(usercode)
			request_codes = [request.my_code for request in friend_requests]
			num_requests = len(request_codes)
			if num_requests == 0:
				request_data = []
			else:
				request_data = UserData.get_by_codes(request_codes)
			self.template_values.update({
				'num_requests': num_requests,
				'request_data': request_data
			})
		
		if not your_friends and userdata.friends_hidden_by_default:
			deny_listing = True
		else:
			deny_listing = False
			friends = Friend.get_who_i_follow(usercode)
			friend_codes = [friend.their_code for friend in friends]
			num_friends = len(friend_codes)
			if num_friends == 0:
				friend_data = []
			else:
				friend_data = UserData.get_by_codes(friend_codes)
			self.template_values.update({
				'num_friends': num_friends,
				'friend_data' : friend_data,
			})
			
		self.template_values.update({
			'nickname': userdata.nickname,
			'your_friends': your_friends,
			'deny_listing' : deny_listing
		})
		
		path = get_template_path('list_friends.html')
		self.response.out.write(template.render(path, self.template_values, debug=True))
		
class RequestFriend(sessions.PersistentRequestHandler):
	def get(self, their_usercode):
		self.init_session()
		if self.do_redirect(): return

		my_usercode = self.get_key('usercode')
		
		if my_usercode is None or their_usercode is None or len(their_usercode) == 0:
			self.restore_previous('Oops! Something went wrong there...')
			return
			
		their_userdata = UserData.get_by_code(their_usercode)
		
		if FriendRequest.already_present(my_usercode, their_usercode):
			self.restore_previous('Your friend request is still awaiting the approval of %s.' % their_userdata.nickname)
			return
		elif FriendRequest.already_present(their_usercode, my_usercode):
			self.redirect(ApproveFriend)
			return
			
		if Friend.already_present(my_usercode, their_usercode):
			self.restore_previous('You and %s are already friends.' % their_userdata.nickname)
			return
			
		FriendRequest.make_request(my_usercode, their_usercode)
		
		self.restore_previous('Friend request sent to %s' % their_userdata.nickname)

class RemoveFriend(sessions.PersistentRequestHandler):
	def get(self, their_usercode):
		self.init_session()
		if self.do_redirect(): return
	
		my_usercode = self.get_key('usercode')
		
		if my_usercode is None or their_usercode is None or len(their_usercode) == 0:
			self.restore_previous('Oops! Something went wrong there...')
			return
		
		their_userdata = UserData.get_by_code(their_usercode)

		if not Friend.already_present(my_usercode, their_usercode):
			self.restore_previous('You and %s are not friends.' % their_userdata.nickname)
			return
		
		FriendRequest.unmake_request(my_usercode, their_usercode)
		FriendRequest.unmake_request(their_usercode, my_usercode)	
		Friend.unmake_friends(my_usercode, their_usercode)
		Friend.unmake_friends(their_usercode, my_usercode)

		self.restore_previous('You are no longer friends with %s' % their_userdata.nickname)
		
	
class ApproveRequest(sessions.PersistentRequestHandler):
	def get(self, their_usercode):
		self.init_session()
		if self.do_redirect(): return
		
		my_usercode = self.get_key('usercode')
		
		if my_usercode is None or their_usercode is None or len(their_usercode) == 0:
			self.restore_previous('Oops! Something went wrong there...')
			return
		
		their_userdata = UserData.get_by_code(their_usercode)

		if Friend.already_present(my_usercode, their_usercode):
			self.restore_previous('You and %s are already friends.' % their_userdata.nickname)
			return

		if not FriendRequest.already_present(their_usercode, my_usercode):
			self.restore_previous('%s has not requested to add you as a friend.' % their_userdata.nickname)
			return

		FriendRequest.unmake_request(my_usercode, their_usercode)
		FriendRequest.unmake_request(their_usercode, my_usercode)
		Friend.make_friends(my_usercode, their_usercode)
		Friend.make_friends(their_usercode, my_usercode)

		self.restore_previous('You are now friends with %s' % their_userdata.nickname)
		
class RejectRequest(sessions.PersistentRequestHandler):
	def get(self, their_usercode):
		self.init_session()
		if self.do_redirect(): return
		
		my_usercode = self.get_key('usercode')
		
		if my_usercode is None or their_usercode is None or len(their_usercode) == 0:
			self.restore_previous('Oops! Something went wrong there...')
			return

		their_userdata = UserData.get_by_code(their_usercode)

		if not FriendRequest.already_present(their_usercode, my_usercode):
			self.restore_previous('%s has not requested to add you as a friend.' % their_userdata.nickname)
			return

		FriendRequest.unmake_request(my_usercode, their_usercode)
		FriendRequest.unmake_request(their_usercode, my_usercode)

		self.restore_previous('You have declined to add %s as your friend.' % their_userdata.nickname)
