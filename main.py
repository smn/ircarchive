# importing django 1.2 for its ObjectPaginator
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from xmpp import XmppHandler
from archive import ArchiveHandler, ChannelHandler, BotHandler, EditChannelHandler
import logging
import backbone

logger = logging.getLogger()
logger.level = logging.DEBUG

application = webapp.WSGIApplication([
        # accept messages via XMPP
        (r'/_ah/xmpp/message/chat/$', XmppHandler),
        (r'/index\.json$', backbone.IndexHandler),
        (r'/channel\.json$', backbone.ChannelHandler),
        (r'/channel/(.+)/(.+)/edit/$', EditChannelHandler),
        (r'/channel/(.+)/(.+)/$', ChannelHandler),
        (r'/bot/', BotHandler),
        (r'/', ArchiveHandler)
    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()