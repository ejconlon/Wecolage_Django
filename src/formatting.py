import pygments, pygments.lexers, pygments.formatters

inited = False

lexdefs = None
formats = None
formats_ordered = None

def init():
	global lexdefs, formats, formats_ordered
	lexdefs = list(pygments.lexers.get_all_lexers())
	formats = dict(((lexdef[0], {}) for lexdef in lexdefs))
	for lexdef in lexdefs:
		longname, shortnames, extensions, mimetypes = lexdef
		formats[longname]['shortname'] = shortnames[0]
		if len(extensions) > 0:
			formats[longname]['extension'] = extensions[0][1:]
		else:
			formats[longname]['extension'] = ''
		if len(mimetypes) > 0:
			formats[longname]['mimetype'] = mimetypes[0]
		else:
			formats[longname]['mimetype'] = 'text/plain'
	formats_ordered = list(formats.keys())
	formats_ordered.sort()

def highlight_with_shortname(content, shortname):
	return pygments.highlight(content,
		pygments.lexers.get_lexer_by_name(shortname), 		
		pygments.formatters.HtmlFormatter()
	)
	
def highlight_with_longname(content, longname):
	return highlight_with_shortname(content, formats[longname]['shortname'])
	
if not inited:
	init()