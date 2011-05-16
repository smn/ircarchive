from django.utils import simplejson as json
from google.appengine.ext import db
from datetime import datetime
import logging

from utils import parse_timestamp, get_or_create

class User(db.Model):
    server = db.StringProperty(required=True)
    nickname = db.StringProperty(required=True)
    created_at = db.DateTimeProperty(required=True, auto_now_add=True)
    last_seen_at = db.DateTimeProperty(required=False)
    
class Channel(db.Model):
    channel = db.StringProperty(required=True)
    server = db.StringProperty(required=True)
    topic = db.TextProperty()
    

class Message(db.Model):
    user = db.ReferenceProperty(User)
    channel = db.ReferenceProperty(Channel)
    timestamp = db.DateTimeProperty(required=True)
    message_type = db.StringProperty(required=True, choices=[
        "system", "action", "message"])
    message_content = db.TextProperty(required=True)
    json = db.TextProperty(required=True)
    
    @staticmethod
    def log(json_data):
        logging.info('Received JSON: %s' % json_data)
        
        payload = json.loads(json_data)
        
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
            message_content=message_content, json=json_data, 
            timestamp=timestamp)
        msg.put()
        return msg
        