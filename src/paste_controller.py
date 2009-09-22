from common import *

import cgi, sessions

from paste_model import Paste

from google.appengine.ext.webapp import template

from reader_controller import Reader
from filer_controller import Filer
from forker_controller import Forker

class Paster(sessions.PersistentRequestHandler):
	def post(self):
		self.init_session()
		if self.do_redirect(): return
		
		paste = Paste()
		paste.usercode = self.get_key('usercode')
		paste.name = cgi.escape(self.request.get('name'))
		paste.content = cgi.escape(self.request.get('content'))
		paste.format = cgi.escape(self.request.get('format'))
		paste.hidden = (self.request.get('hidden')=="on")
		paste.parsed_content = formatting.highlight_with_longname(
								self.request.get('content'), paste.format)
		
		paste.save_new(cgi.escape(self.request.get('password')))
		
		self.session['flash'] = 'Pasted sucessfully.'
		self.redirect('/paste/'+paste.pastecode)

	def get(self):
		self.init_session()
		if self.do_redirect(): return
		
		self.template_values.update({
			'formats': formatting.formats_ordered
		})
		
		path = get_template_path('new_paste.html')
		self.response.out.write(template.render(path, self.template_values, debug=True))