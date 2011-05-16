from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import xmpp_handlers
from models import User, Channel, Message
from django.utils import simplejson as json
from datetime import datetime
import logging

"""
sample json:

{
    "nickname": "sdehaan",
    "server": "irc.freenode.net",
    "channel": "#vumi",
    "message_type": "message",
    "message_content": "testing app engine",
    "timestamp": "2011-05-16T08:17:53.749184"
}

"""

def key(*args):
    return db.Key.from_path(*args)

def get_or_create(model, **kwargs):
    # recreating get_or_insert, I must be doing something wrong
    def txn():
        key_name = key(model.kind(), '/'.join(kwargs.values())).id_or_name()
        entity = model.get_by_key_name(key_name)
        if entity is None:
            entity = model(key_name=key_name, **kwargs)
            entity.put()
        return entity
    return db.run_in_transaction(txn)

def parse_timestamp(timestamp):
    FORMAT = '%Y-%m-%dT%H:%M:%S'
    if '.' in timestamp:
        nofrag, frag = timestamp.split('.')
        nofrag_dt = datetime.strptime(nofrag, FORMAT)
        dt = nofrag_dt.replace(microsecond=int(frag))
        return dt
    else:
        return datetime.strptime(timestamp, FORMAT)

class XmppHandler(xmpp_handlers.CommandHandler):
    def text_message(self, message=None):
        payload = json.loads(message.body)
        
        # get the payload data
        nickname = payload.get('nickname')
        server = payload.get('server', 'unknown')
        channel = payload.get('channel')
        message_type = payload.get('message_type')
        message_content = payload.get('message_content')
        timestamp = parse_timestamp(payload.get('timestamp'))
        
        user = get_or_create(User, server=server, nickname=nickname)
        user.last_seen_at = datetime.utcnow()
        user.put()
        
        channel = get_or_create(Channel, server=server, channel=channel)
        # store the message
        msg = Message(user=user, channel=channel, message_type=message_type,
            message_content=message_content, json=message.body, 
            timestamp=timestamp)
        msg.put()

application = webapp.WSGIApplication([
        ('/_ah/xmpp/message/chat/', XmppHandler)
    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()