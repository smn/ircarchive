from django.utils import simplejson as json
from google.appengine.ext import db
from datetime import datetime
from urllib2 import unquote
import logging

from utils import parse_timestamp, get_or_create, prefetch_refprops
import color

class User(db.Model):
    
    server = db.StringProperty(required=True)
    nickname = db.StringProperty(required=True)
    created_at = db.DateTimeProperty(required=True, auto_now_add=True)
    last_seen_at = db.DateTimeProperty(required=False)
    color = db.ListProperty(int, required=True, default=[])
    is_human = db.BooleanProperty(required=True, default=True)
    
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
    username = db.StringProperty(required=False, default='')
    password = db.StringProperty(required=False, default='')
    topic = db.TextProperty()
    
    def is_private(self):
        return self.username and self.password
    
    def authenticate(self, username, password):
        return username == self.username and password == self.password
    
    def to_dict(self):
        return dict([(p, getattr(self, p)) 
                for p in self.properties()])
    
    @classmethod
    def list(cls, prefix="#"):
        channels = [channel for channel in Channel.all().order('channel')]
        if prefix:
            channels = filter(lambda c: c.channel.startswith(prefix), channels)
        return channels
    
    @classmethod
    def find(cls, server, channel):
        key = db.Key.from_path(Channel.kind(), '%s/%s' % (unquote(channel), server))
        return Channel.get(key)
    

class Message(db.Model):
    user = db.ReferenceProperty(User)
    user_is_human = db.BooleanProperty(required=True, default=True)
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
            timestamp=timestamp, user_is_human = user.is_human)
        msg.put()
        return msg
        