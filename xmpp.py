from google.appengine.ext.webapp import xmpp_handlers
from models import User, Channel, Message
from django.utils import simplejson as json
from utils import parse_timestamp, get_or_create
from datetime import datetime

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
