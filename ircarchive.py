from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import xmpp_handlers
from models import User, Channel, Message
import json
from datetime import datetime

class XmppHandler(xmpp_handlers.CommandHandler):
    def text_message(self, message=None):
        payload = json.loads(message.body)
        
        # get the payload data
        username = payload.get('username')
        server = payload.get('server', 'unknown')
        channel = payload.get('channel')
        message_type = payload.get('message_type')
        message_content = payload.get('message_content')
        timestamp = payload.get('timestamp')
        
        # store the message
        msg = Message()
        msg.user = User.find_by_username(server, username)
        msg.channel = Channel.find_channel(server, channel)
        msg.message_type = message_type
        msg.message_content = message_content
        msg.json = message.body
        msg.put()
        
        msg.reply('thanks!')

application = webapp.WSGIApplication([
        ('/_ah/xmpp/message/chat/', XmppHandler)
    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()