from common import *

import cgi, formatting
#import sessions

from django.shortcuts import render_to_response

from paste_model import Paste

def home(request):  
	#session = sessions.Session(request)
	#if session.do_redirect(): return
	template_values = {}
	
	pastes = Paste.get_most_recent_public()
		
	template_values.update({
		'explain': True,
		'formats': formatting.formats_ordered,
		'pastes': pastes
	})
	return render_to_response('index.html', template_values)
		
# class About(sessions.PersistentRequestHandler):  
# 	def get(self):
# 		self.init_session()
# 		if self.do_redirect(): return
# 		path = get_template_path('about.html')
# 		self.response.out.write(template.render(path, self.template_values, debug=True))
# 
# class FourOhFour(sessions.PersistentRequestHandler):  
# 	def get(self):
# 		self.init_session()
# 		if self.do_redirect(): return
# 		self.error(404)
# 		path = get_template_path('404.html')
# 		self.response.out.write(template.render(path, self.template_values, debug=True))
# 		
# class Login(sessions.PersistentRequestHandler):  
# 	def get(self):
# 		self.init_session()
# 		if 'previous' in self.session:
# 			previous = self.session['previous']
# 			self.session.delete_item('previous')
# 		else:
# 			previous = '/profile'
# 		self.session.delete_item('current')
# 		self.redirect(users.create_login_url(previous))
# 		return
# 		
# class Logout(sessions.PersistentRequestHandler):  
# 	def get(self):
# 		self.init_session()
# 		if 'previous' in self.session:
# 			previous = self.session['previous']
# 			#self.session.delete_item('previous')
# 		else:
# 			previous = '/profile'
# 		#self.session.delete_item('current')
# 		self.session.delete()
# 		self.session = None
# 		self.redirect(users.create_logout_url(previous))
# 		return