from google.appengine.ext import db

class User(db.Model):
    nickname = db.StringProperty(required=True)
    created_at = db.DateTimeProperty(required, auto_now_add=True)
    last_seen_at = db.DateTimeProperty(required)

class Channel(db.Model):
    channel = db.StringProperty(required=True)
    server = db.StringProperty(required=True)
    topic = db.TextProperty()

class Message(db.Model):
    user = db.ReferencePropery(User)
    channel = db.ReferencePropery(Channel)
    timestamp = db.DateTimeProperty(required)
    message_type = db.StringProperty(required=True, choices=[
        "system", "action", "message"])
    message_content = db.TextProperty(required=True)