from google.appengine.ext import db
from datetime import datetime

def key(*args):
    return db.Key.from_path(*args)

class User(db.Model):
    server = db.StringProperty(required=True)
    nickname = db.StringProperty(required=True)
    created_at = db.DateTimeProperty(required, auto_now_add=True)
    last_seen_at = db.DateTimeProperty(required)
    
    @staticmethod
    def find_by_nickname(server, nickname):
        user = User.get(key(User.kind(), server, nickname))
        if user is None:
            user = User()
            user.server = server
            user.nickname = nickname
            user.last_seen_at = datetime.now()
            user.put()
        return user

class Channel(db.Model):
    channel = db.StringProperty(required=True)
    server = db.StringProperty(required=True)
    topic = db.TextProperty()
    
    @staticmethod
    def find_channel(server, channel):
        channel = Channel.get(key(Channel.kind(), server, channel))
        if channel is None:
            channel = Channel()
            channel.server = server
            channel.channel = channel
            channel.put()
        return channel

class Message(db.Model):
    user = db.ReferencePropery(User)
    channel = db.ReferencePropery(Channel)
    timestamp = db.DateTimeProperty(required=True)
    message_type = db.StringProperty(required=True, choices=[
        "system", "action", "message"])
    message_content = db.TextProperty(required=True)
    json = db.TextProperty(required=True)