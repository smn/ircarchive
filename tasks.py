# importing django 1.2 for its ObjectPaginator
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from archive import LogSweepHandler, BotFlaggingHandler, ClearHandler

application = webapp.WSGIApplication([
        ('/tasks/log/sweeper/', LogSweepHandler),
        ('/tasks/bot/flagger/', BotFlaggingHandler),
        ('/tasks/clear/', ClearHandler)
    ], debug=True)
