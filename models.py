from django.utils import simplejson as json
from google.appengine.ext import db
from datetime import datetime
from urllib2 import unquote
import logging

from utils import parse_timestamp, get_or_create, prefetch_refprops
import color

class Tag(db.Model):
    name = db.StringProperty(required=True)
    
    @staticmethod
    def get_or_create(*tags):
        tag_names = set([tag.strip() for tag in tags])
        return [get_or_create(Tag, name=name) for name in tag_names]
    

class User(db.Model):
    
    server = db.StringProperty(required=True)
    nickname = db.StringProperty(required=True)
    created_at = db.DateTimeProperty(required=True, auto_now_add=True)
    last_seen_at = db.DateTimeProperty(required=False)
    color = db.ListProperty(int, required=True, default=[])
    tags = db.ListProperty(db.Key, required=True, default=[])
    
    @staticmethod
    def find(server, nickname):
        key = db.Key.from_path(User.kind(), '%s/%s' % (nickname, server))
        return User.get(key)
    
    def get_color(self):
        if not self.color:
            self.color = color.random()
            self.put()
        return self.color
    
class Channel(db.Model):
    channel = db.StringProperty(required=True)
    server = db.StringProperty(required=True)
    topic = db.TextProperty()
    
    @staticmethod
    def find(server, channel):
        key = db.Key.from_path(Channel.kind(), '%s/%s' % (unquote(channel), server))
        return Channel.get(key)
    

class Message(db.Model):
    user = db.ReferenceProperty(User)
    channel = db.ReferenceProperty(Channel)
    timestamp = db.DateTimeProperty(required=True)
    message_type = db.StringProperty(required=True, choices=[
        "system", "action", "message"])
    message_content = db.TextProperty(required=True)
    json = db.TextProperty(required=True)
    tags = db.ListProperty(db.Key, required=True, default=[])
    
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
            timestamp=timestamp,tags=user.tags)
        msg.put()
        return msg
        