
import cgi, os, hashlib, formatting, random, logging

usercode_len = 8
pastecode_len = 8
apikey_len = 64
max_code_len = max(usercode_len, pastecode_len, apikey_len)

filename_chars = set("012345789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ._-")

def sub_char(c):
	if c in filename_chars:
		return c
	else:
		return "_"
	
def make_filename(s):
	fn = "".join((sub_char(c) for c in s))
	if len(fn) == 0:
		return "wecolage_file"
	else:
		return fn
		
def sha1(s):
	return hashlib.sha1(s).hexdigest()

def has_extension(s):
	return len(s.split('.'))>1

#def get_login_link(user, request_uri):
#	if user:
#		url = users.create_logout_url(request_uri)
#		url_linktext = 'Logout'	
#	else:
#		url = users.create_login_url(request_uri)
#		url_linktext = 'Login'
#	return url, url_linktext

def get_template_path(template):
	return os.path.join(os.path.dirname(__file__),
						'../templates/' + template)

#def add_template_values(d, user, request_uri):
#	d['formats'] = formatting.formats_ordered
#	if user:
#		d['username'] = user.nickname()
#	login_url, login_url_linktext = get_login_link(user, request_uri)
#	d['login_url'] = login_url
#	d['login_url_linktext'] = login_url_linktext
#	return d
