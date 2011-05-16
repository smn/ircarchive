from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from xmpp import XmppHandler
from archive import ArchiveHandler

"""
Sample json received via XMPP:

{
    "nickname": "sdehaan",
    "server": "irc.freenode.net",
    "channel": "#vumi",
    "message_type": "message",
    "message_content": "testing app engine",
    "timestamp": "2011-05-16T08:17:53.749184"
}

"""

application = webapp.WSGIApplication([
        ('/_ah/xmpp/message/chat/', XmppHandler),
        ('/', ArchiveHandler)
    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()