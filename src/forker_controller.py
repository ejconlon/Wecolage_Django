from common import *

import cgi, sessions, difflib, formatting

from paste_model import Paste

from google.appengine.ext.webapp import template

class Forker(sessions.PersistentRequestHandler):
	def get(self, code):
		self.init_session()
		if self.do_redirect(): return
		
		paste = Paste.get_by_code(cgi.escape(code))
		if paste is None:
			logger.error("PASTE "+code+" NOT FOUND")
			self.redirect('/404')
			return
		
		self.template_values.update({
			'formats': formatting.formats_ordered,
			'paste': paste,
			'paste_url': paste.get_url()
		})
		
		path = get_template_path('edit_paste.html')
		self.response.out.write(template.render(path, self.template_values, debug=True))
		
	def post(self, code):
		self.init_session()
		if self.do_redirect(): return
		
		old_code = cgi.escape(self.request.get('old_code'))
		
		old_paste = Paste.get_by_code(old_code)
		if old_paste is None:
			logger.error("PASTE "+old_code+" NOT FOUND")
			self.redirect('/404')
			return
		
		user = self.get_key('user')
		paste = old_paste.start_fork(user)
		paste.name = cgi.escape(self.request.get('name'))
		paste.content = cgi.escape(self.request.get('content'))
		paste.hidden = (cgi.escape(self.request.get('hidden'))=="on")
		paste.format = cgi.escape(self.request.get('format'))
		paste.parsed_content = formatting.highlight_with_longname(
								self.request.get('content'), paste.format)
		paste.parent_diff = "".join(difflib.unified_diff(
			old_paste.content.split('\n'),
			paste.content.split('\n')
		))
		paste.parsed_parent_diff = formatting.highlight_with_shortname(paste.parent_diff, 'diff')
		paste.save_new(cgi.escape(self.request.get('password')))
		
		self.session['flash'] = 'Forked successfully.'
		self.redirect('/paste/'+paste.pastecode)