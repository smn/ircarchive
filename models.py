from google.appengine.ext import db
from datetime import datetime

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