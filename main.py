import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ircarchive.settings'

from django.core.handlers import wsgi
app = wsgi.WSGIHandler()
