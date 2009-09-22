from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin
from django.contrib import admin
admin.autodiscover()

import wecolage.home_controller

urlpatterns = patterns('',
    # Example:
    #(r'^wecolage/', include('wecolage.foo.urls')),

	(r'^$', 'wecolage.home_controller.home'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc2/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin2/', include(admin.site.urls)),

	#(r'.*', '404')
)
