from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import xmpp_handlers
from models import User, Channel, Message
import json

class XmppHandler(xmpp_handlers.CommandHandler):
    def text_message(self, message=None):
        payload = json.loads(message.body)

application = webapp.WSGIApplication([], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()