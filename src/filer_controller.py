from common import *

import cgi, sessions

from paste_model import Paste

from google.appengine.ext.webapp import template

class Filer(sessions.PersistentRequestHandler):
	def get(self, code, filename=None):
		self.init_session()
		if self.do_redirect(): return
		
		paste = Paste.get_by_code(code)
		if paste is None:
			logger.error("PASTE "+code+" NOT FOUND")
			self.redirect('/404')
			return
		
		if filename is None:
			filename = make_filename(paste.name)
			if not has_extension(filename):
				filename += formatting.formats[paste.format]['extension']
			self.redirect('/paste/'+code+'/download/'+filename)
			return
		elif filename[0] == '/':
			filename = filename[1:]
		
		self.response.headers['Content-type'] = formatting.formats[paste.format]['mimetype']
		path = get_template_path('file_out')
		self.response.out.write(template.render(path, {'content':paste.content}, debug=True))
