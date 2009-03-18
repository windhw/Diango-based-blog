from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:


urlpatterns = patterns('',
    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^survey/$', 'survey.views.index'),
    (r'^survey/submit$', 'survey.views.submit'),
    (r'^.*$','blog.views.notexist')
)
