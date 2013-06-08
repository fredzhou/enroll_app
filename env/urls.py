from django.conf.urls import patterns, include, url
from enroll_app import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'first.views.home', name='home'),
    # url(r'^first/', include('first.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^enroll/$', views.enroll),
    url(r'.*', views.enroll),
)
