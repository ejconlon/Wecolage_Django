# (c) Copyright 2007 Thomas Bohmbach, Jr.  All Rights Reserved. 
#
# See the LICENSE file that should have been included with this distribution
# for more specific information.

import re, urllib, urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site, RequestSite
from django.core.urlresolvers import get_callable
from django.db.models import permalink
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.encoding import iri_to_uri
from openid.consumer.consumer import Consumer, SUCCESS, CANCEL, FAILURE, SETUP_NEEDED
from django_openidconsumer.util import DjangoOpenIDStore, from_openid_response

from openid_auth import OPENIDS_SESSION_NAME, OPENID_ERROR_SESSION_NAME
from openid_auth.forms import OpenIDLoginForm, OpenIDCreateForm, OPENID_FORM_FIELD_NAME, NEXT_FORM_FIELD_NAME
from openid_auth.models import UserOpenID

try:
    # The mod_python version is more efficient, so try importing it first.
    from mod_python.util import parse_qsl
except ImportError:
    from cgi import parse_qsl


def get_view(lookup_view):
    """
    Returns the callable function represented by ``lookup_view``.  If it's a string,
    it will try to resolve it into a callable using the same logic as
    ``django.core.urlresolvers``.  If it's already a callable, it simply
    returns ``lookup_view``.
    """
    try:
        return get_callable(lookup_view)
    except ImportError, e:
        mod_name, _ = get_mod_func(lookup_view)
        raise ViewDoesNotExist, "Could not import %s. Error was: %s" % (mod_name, str(e))
    except AttributeError, e:
        mod_name, func_name = get_mod_func(lookup_view)
        raise ViewDoesNotExist, "Tried %s in module %s. Error was: %s" % (func_name, mod_name, str(e))

redirect_url_re = re.compile('^/[-\w/]+$')
def is_valid_redirect_url(redirect):
    """
    Restrict the URL to being a local path, not a complete URL.
    """
    return bool(redirect_url_re.match(redirect))

def get_openid_return_host(request):
    """
    Get the complete host URL.
    """
    host = getattr(settings, 'OPENID_RETURN_HOST', None)
    if not host:
        if request.is_secure():
            scheme = 'https'
        else:
            scheme = 'http'
        host = urlparse.urlunsplit((scheme, request.get_host(), '', '', ''))
    return host

@permalink
def get_openid_return_path(return_view_name):
    """
    Reverse URL lookup (permalink) for a given OpenID return view.
    """
    return (return_view_name,)

def get_openid_return_url(request,
        return_view_name='openid_auth-complete_openid_login',
        redirect_field_name=REDIRECT_FIELD_NAME,
        redirect=None):
    """
    Get the URL to tell the openid server to redirect back to and, if
    available, append the redirect query parameter.
    """
    url = urlparse.urljoin(get_openid_return_host(request),
                           get_openid_return_path(return_view_name))
    (scheme, location, path, query, fragment) = urlparse.urlsplit(url)
    #If a 'redirect' attribute is provided, append that to the openid_return_url
    if redirect and is_valid_redirect_url(redirect):
        query_kv = parse_qsl(query)
        query_kv.append((redirect_field_name, redirect))
        query = urllib.urlencode(query_kv)
    return iri_to_uri(urlparse.urlunsplit((scheme, location, path, query, fragment)))

def login(request, template_name='accounts/login.html', redirect_field_name=REDIRECT_FIELD_NAME):
    if request.POST:
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        if username or password:
            return login_auth(request, template_name=template_name, redirect_field_name=redirect_field_name)
        else:
            return login_openid(request, template_name=template_name, redirect_field_name=redirect_field_name)
    else:
        openid_url = request.GET.get(OPENID_FORM_FIELD_NAME, '')
        if openid_url:
            return login_openid(request, template_name=template_name, redirect_field_name=redirect_field_name)
        else:
            return login_auth(request, template_name=template_name, redirect_field_name=redirect_field_name)

def login_auth(request, template_name='accounts/login_auth.html', redirect_field_name=REDIRECT_FIELD_NAME):
    """
    This starts the auth (traditional) login process.
    """
    return auth_views.login(request, template_name=template_name, redirect_field_name=redirect_field_name)

def login_openid(request, template_name='accounts/login_openid.html', redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Displays the OpenID login form and handles the OpenID login action.
    
    ``redirect_field_name`` must be set to the same value as that passed into
    the ``complete_openid_login`` view.
    """
    openid_error = request.session.get(OPENID_ERROR_SESSION_NAME, '')
    openid_url = request.REQUEST.get(OPENID_FORM_FIELD_NAME, 'http://')
    #Was the form submitted?
    if request.POST:
        redirect = request.POST.get(NEXT_FORM_FIELD_NAME, '')
        request.session[OPENID_ERROR_SESSION_NAME] = ''
        openid_form = OpenIDLoginForm(request.POST)
        if openid_form.is_valid(request=request):
            request.session.delete_test_cookie()
            return begin_openid(request, openid_url, redirect_field_name=redirect_field_name, redirect=redirect)
    #Did we submit the form, go to the OpenID server, and return with an error?
    elif openid_error:
        request.session.set_test_cookie()
        redirect = request.GET.get(redirect_field_name, '')
        openid_form = OpenIDLoginForm({OPENID_FORM_FIELD_NAME : openid_url,
                                       NEXT_FORM_FIELD_NAME : redirect})
        openid_form.is_valid(request=request)    #This will result in the openid_error becoming a form error
        request.session[OPENID_ERROR_SESSION_NAME] = ''
    #We're displaying this page for the first time
    else:
        request.session.set_test_cookie()
        redirect = request.GET.get(redirect_field_name, '')
        openid_form = OpenIDLoginForm(initial={OPENID_FORM_FIELD_NAME : openid_url,
                                               NEXT_FORM_FIELD_NAME : redirect})
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)
    return render_to_response(template_name,
                              {'openid_form' : openid_form,
                               'site_name' : current_site.name,
                               redirect_field_name : redirect},
                              context_instance=RequestContext(request))

def begin_openid(request, openid_url,
        redirect_field_name=REDIRECT_FIELD_NAME, redirect=None,
        return_view_name='openid_auth-complete_openid_login',
        sreg=None, extension_args=None):
    """
    Setup the openid Consumer and redirect to the openid URL.
    """
    #Set up the openid authorization request
    consumer = Consumer(request.session, DjangoOpenIDStore())
    openid_auth = consumer.begin(openid_url)
    #Add openid extension args (for things like simple registration)
    extension_args = extension_args or {}
    #If we want simple registration, set the correct extension argument
    if sreg:
        extension_args['sreg.optional'] = sreg
    for name, value in extension_args.items():
        namespace, key = name.split('.', 1)
        openid_auth.addExtensionArg(namespace, key, value)
    #Get the host to authenticate for
    trust_root = getattr(settings, 'OPENID_TRUST_ROOT', get_openid_return_host(request) + '/')
    #Make sure we have a full return URL and that we append any redirect parameters to it
    openid_return_url = get_openid_return_url(request,
                                              return_view_name=return_view_name,
                                              redirect_field_name=redirect_field_name,
                                              redirect=redirect)
    #Redirect to the authentication service
    openid_redirect_url = openid_auth.redirectURL(trust_root, openid_return_url)
    return HttpResponseRedirect(openid_redirect_url)

def complete_openid(request, success_view, failure_view, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    The openid callback utility view.
    
    ``redirect_field_name`` must be set to the same value as that passed into
    the ``begin_openid`` view that initiates the openid call.
    """
    success_view = get_view(success_view)
    failure_view = get_view(failure_view)
    #Get the openid response
    consumer = Consumer(request.session, DjangoOpenIDStore())
    openid_response = consumer.complete(dict(request.GET.items()))
    #Deal with the response based on status
    if openid_response.status == SUCCESS:
        return success_view(request, openid_response, redirect_field_name=redirect_field_name)
    else:
        if openid_response.status == CANCEL:
            error_message = _("The request was cancelled.")
        elif openid_response.status == FAILURE:
            error_message = _(openid_response.message)
        elif openid_response.status == SETUP_NEEDED:
            error_message = _("Setup needed.  Please check your OpenID provider and try again.")
        else:
            error_message = "%s: %s" % (_("Bad openid status"), openid_response.status)
        return failure_view(request, openid_response, error_message, redirect_field_name=redirect_field_name)

def success_openid_login(request, openid_response, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    A view-helper to handle a successful OpenID authentication response.  Note that this
    doesn't mean we've found a matching user yet.  That's what this method
    does.  This view-helper requires adding ``openid_auth.models.OpenIDBackend`` to the
    ``settings.AUTHENTICATION_BACKENDS`` list.
    """
    #Get the OpenID URL
    openid_url = openid_response.identity_url
    #Call the built in django auth function
    #(NOTE: this call won't work without adding 'openid_auth.models.OpenIDBackend' to the settings.AUTHENTICATION_BACKENDS list)
    user = authenticate(openid_url=openid_url)
    if user:
        #Log in the user with the built-in django function
        auth_login(request, user)
        #Do we not yet have any openids in the session?
        if OPENIDS_SESSION_NAME not in request.session.keys():
            request.session[OPENIDS_SESSION_NAME] = []
        #Eliminate any duplicate openids in the session
        request.session[OPENIDS_SESSION_NAME] = [o for o in request.session[OPENIDS_SESSION_NAME] if o.openid != openid_url]
        #Add this new openid to the list
        request.session[OPENIDS_SESSION_NAME].append(from_openid_response(openid_response))
        #Get the page to redirect to
        redirect = request.REQUEST.get(redirect_field_name, None)
        if not redirect or not is_valid_redirect_url(redirect):
            redirect = settings.LOGIN_REDIRECT_URL
        return HttpResponseRedirect(redirect)
    else:
        #TODO: This should start the registration process
        return failure_openid_login(request,
                                    openid_response,
                                    _("The OpenID doesn't match any registered user."),
                                    redirect_field_name=REDIRECT_FIELD_NAME)

def failure_openid_login(request, openid_response, error_message, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    A view-helper to handle a failed openid login authentication.
    """
    openid_url = openid_response.identity_url
    login_url = settings.LOGIN_URL
    (scheme, location, path, query, fragment) = urlparse.urlsplit(login_url)
    query_kv = []
    if openid_url:
        query_kv.append((OPENID_FORM_FIELD_NAME, openid_url))
    redirect = request.GET.get(redirect_field_name, None)
    if redirect:
        query_kv.append((redirect_field_name, redirect))
    query = urllib.urlencode(query_kv)
    login_url = urlparse.urlunsplit((scheme, location, path, query, fragment))
    request.session[OPENID_ERROR_SESSION_NAME] = error_message
    return HttpResponseRedirect(login_url)

def logout(request, next_page=None, template_name='accounts/logged_out.html'):
    """
    View to handle loging a user out.
    """
    if OPENIDS_SESSION_NAME in request.session.keys():
        request.session[OPENIDS_SESSION_NAME] = []
    return auth_views.logout(request, next_page=next_page, template_name=template_name)

@login_required
def create_openid(request, template_name='accounts/openid_form.html',
        extra_context=None, redirect_field_name=REDIRECT_FIELD_NAME,
        redirect=None, verify=True):
    """
    Generic view that optionally verifies and adds an openid to the currently logged in user.
    """
    if extra_context is None: extra_context = {}
    openid_error = request.session.get(OPENID_ERROR_SESSION_NAME, '')
    openid_url = request.REQUEST.get(OPENID_FORM_FIELD_NAME, 'http://')
    #Was the form submitted?
    if request.POST:
        if not redirect:
            redirect = request.POST.get(NEXT_FORM_FIELD_NAME, '')
        request.session[OPENID_ERROR_SESSION_NAME] = ''
        openid_form = OpenIDCreateForm(request.POST)
        if openid_form.is_valid(request=request):
            if verify:
                return begin_openid(request, openid_url,
                                             redirect_field_name=redirect_field_name,
                                             redirect=redirect,
                                             return_view_name='openid_auth-complete_openid_create')
            else:
                return success_openid_create(request, openid_url, redirect=redirect)
    #Did we submit the form, go to the OpenID server, and return with an error?
    elif openid_error:
        if not redirect:
            redirect = request.GET.get(redirect_field_name, '')
        openid_form = OpenIDCreateForm({OPENID_FORM_FIELD_NAME : openid_url,
                                        NEXT_FORM_FIELD_NAME : redirect})
        openid_form.is_valid(request=request)    #This will result in the openid_error becoming a form error
        request.session[OPENID_ERROR_SESSION_NAME] = ''
    #We're displaying this page for the first time
    else:
        if not redirect:
            redirect = request.GET.get(redirect_field_name, '')
        openid_form = OpenIDCreateForm(initial={OPENID_FORM_FIELD_NAME : openid_url,
                                                NEXT_FORM_FIELD_NAME : redirect})
    context = RequestContext(request)
    for key, value in extra_context.items():
        if callable(value):
            context[key] = value()
        else:
            context[key] = value
    return render_to_response(template_name,
                              {'openid_form' : openid_form,
                               redirect_field_name : redirect},
                              context_instance=context)

def success_openid_create(request, openid_response, redirect_field_name=REDIRECT_FIELD_NAME, redirect=None):
    """
    A view-helper to handle a successful OpenID authentication response for a
    create openid call.
    """
    #Get the OpenID URL
    openid_url = openid_response.identity_url
    user = request.user
    if user.is_authenticated:
        try:
            user_openid = UserOpenID.objects.get(openid_url=openid_url)
        except UserOpenID.DoesNotExist:
            user_openid = None
        #Check to see if this OpenID URL is already registered
        if user_openid:
            if user_openid.user == user:
                message = _('That OpenID URL is already registered to you')
            else:
                message = _('That OpenID URL is already registered')
            return failure_openid_create(request, openid_response, message, redirect_field_name=REDIRECT_FIELD_NAME, redirect=None)
        #Add the openid_url to the user's account
        try:
            user.openids.create(openid_url=openid_url)
        except Exception, e:
            return failure_openid_create(request, openid_response, _(str(e)), redirect_field_name=REDIRECT_FIELD_NAME, redirect=None)
        #Get the page to redirect to
        if not redirect:
            redirect = request.REQUEST.get(redirect_field_name, None)
            if not redirect or not is_valid_redirect_url(redirect):
                redirect = getattr(settings, 'CREATE_OPENID_REDIRECT_URL', None)
                if not redirect or not is_valid_redirect_url(redirect):
                    redirect = '/accounts/openid_create/'
        message = _("OpenID (%s) added successfully.") % openid_url
        user.message_set.create(message=message)
        return HttpResponseRedirect(redirect)
    else:
        return failure_openid_create(request, openid_url, _("No logged in user to add the OpenID to."))

def failure_openid_create(request, openid_response, error_message,
        redirect_field_name=REDIRECT_FIELD_NAME, redirect=None):
    """
    A view-helper to handle a failed create openid authentication.
    """
    openid_url = openid_response.identity_url
    create_openid_url = getattr(settings, 'CREATE_OPENID_URL', None)
    if not create_openid_url or not is_valid_redirect_url(create_openid_url):
        create_openid_url = '/accounts/openid_create/'
    (scheme, location, path, query, fragment) = urlparse.urlsplit(create_openid_url)
    query_kv = []
    if openid_url:
        query_kv.append((OPENID_FORM_FIELD_NAME, openid_url))
    if not redirect:
        redirect = request.GET.get(redirect_field_name, None)
    if redirect:
        query_kv.append((redirect_field_name, redirect))
    query = urllib.urlencode(query_kv)
    create_openid_url = urlparse.urlunsplit((scheme, location, path, query, fragment))
    request.session[OPENID_ERROR_SESSION_NAME] = error_message
    return HttpResponseRedirect(create_openid_url)

def delete_openid(request, user_openid_id, redirect,
        template_name='accounts/openid_confirm_delete.html',
        extra_context=None):
    """
    UserOpenID delete function.
    
    The given template will be used to confirm deletetion if this view is
    fetched using GET; for safty, deletion will only be performed if this
    view is POSTed.
    
    Templates: ``accounts/openid_confirm_delete.html``
    RequestContext:
        user_openid
            the UserOpenID object being deleted
    """
    user = request.user
    if extra_context is None: extra_context = {}
    try:
        user_openid = UserOpenID.objects.get(id=user_openid_id, user=user)
    except UserOpenID.DoesNotExist:
        raise Http404, _("No UserOpenID found for %s with id=%s") % (user, user_openid_id)
    if request.method == 'POST':
        openid_url = user_openid.openid_url
        user_openid.delete()
        request.user.message_set.create(message=_("The OpenID (%s) was removed.") % openid_url)
        return HttpResponseRedirect(redirect)
    else:
        context = RequestContext(request)
        for key, value in extra_context.items():
            if callable(value):
                context[key] = value()
            else:
                context[key] = value
        return render_to_response(template_name,
                                  {'user_openid' : user_openid},
                                  context_instance=context)

