from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from xmpp import XmppHandler
from archive import ArchiveHandler

application = webapp.WSGIApplication([
        ('/_ah/xmpp/message/chat/', XmppHandler),
        ('/', ArchiveHandler)
    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()