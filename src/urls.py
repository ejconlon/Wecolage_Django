from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin
from django.contrib import admin
admin.autodiscover()

import wecolage.home_controller
import wecolage.auth_controller

urlpatterns = patterns('',
    # Example:
    #(r'^wecolage/', include('wecolage.foo.urls')),

	(r'^$', 'wecolage.home_controller.home'),

	(r'^accounts/login/?$', 'wecolage.auth_controller.login'),
	(r'^accounts/login_openid/?$', 'wecolage.auth_controller.login_openid'),
	(r'^accounts/login_auth/?$', 'wecolage.auth_controller.login_auth'),
	(r'^openid/complete/?$', 'wecolage.auth_controller.complete_openid_login'),
	(r'^accounts/logout/?$', 'wecolage.auth_controller.logout', {'next_page' : '/'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

	#(r'.*', '404')
)
