from common import *

import cgi, sessions

from paste_model import Paste

from google.appengine.ext.webapp import template

class Reader(sessions.PersistentRequestHandler):
	def get(self, code):
		self.init_session()
		if self.do_redirect(): return
		
		paste = Paste.get_by_code(cgi.escape(code))
		if paste is None:
			logger.error("PASTE "+code+" NOT FOUND")
			self.redirect('/404')
			return
			
		self.template_values.update({
			'paste': paste,
			'paste_url': paste.get_url()
		})
		
		path = get_template_path('view_paste.html')
		self.response.out.write(template.render(path, self.template_values, debug=True))