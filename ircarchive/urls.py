from django.conf.urls.defaults import patterns, url
from ircarchive.base import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
)
