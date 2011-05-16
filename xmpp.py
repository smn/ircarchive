from google.appengine.ext import db
from google.appengine.ext.webapp import xmpp_handlers
from models import User, Channel, Message
from django.utils import simplejson as json
from utils import parse_timestamp, get_or_create
from datetime import datetime
import logging

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

class XmppHandler(xmpp_handlers.CommandHandler):
    def text_message(self, message=None):
        im_from = db.IM("xmpp", message.sender)
        
        # only accept from XMPP messages from our domain
        if '@praekeltfoundation.org/' not in im_from.address:
            return
        
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
