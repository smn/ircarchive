import logging

from datetime import datetime
from urllib2 import unquote

from django.utils import simplejson as json

from google.appengine.ext import db, search

from ircarchive.base.utils import (parse_timestamp, parse_vumi_timestamp,
    get_or_create)
from ircarchive.base import color


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

    @staticmethod
    def find(server, channel):
        key = db.Key.from_path(Channel.kind(), '%s/%s' % (unquote(channel),
            server))
        return Channel.get(key)


class Message(search.SearchableModel):
    user = db.ReferenceProperty(User)
    user_is_human = db.BooleanProperty(required=True, default=True)
    channel = db.ReferenceProperty(Channel)
    timestamp = db.DateTimeProperty(required=True)
    message_type = db.StringProperty(required=True, choices=[
        "system", "action", "message"], indexed=False)
    message_content = db.TextProperty(required=True, indexed=False)

    json = db.TextProperty(required=True, indexed=False)

    @classmethod
    def SearchableProperties(cls):
        return [['message_content']]

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
            timestamp=timestamp, user_is_human=user.is_human)
        msg.put()
        return msg

    @staticmethod
    def log_common_message_format(json_data):
        logging.info("Received JSON: %s" % json_data)
        msg = json.loads(json_data)
        nickname = msg['from_addr']
        irc_metadata = msg['helper_metadata'].get('irc', {})

        server_and_port = irc_metadata.get('irc_server')
        server = server_and_port.partition(':')[0]
        channel = irc_metadata.get('irc_channel')

        command_map = {
            'PRIVMSG': 'message',
            'ACTION': 'action'
        }

        irc_command = irc_metadata.get('irc_command', 'PRIVMSG')
        message_content = msg['content']
        message_type = command_map.get(irc_command)

        if message_type and channel:
            timestamp = parse_vumi_timestamp(msg['timestamp'])

            user = get_or_create(User, server=server, nickname=nickname)
            user.last_seen_at = datetime.utcnow()
            user.put()

            channel = get_or_create(Channel, server=server, channel=channel)
            msg = Message(user=user, channel=channel,
                message_type=message_type, message_content=message_content,
                json=json_data, timestamp=timestamp,
                user_is_human=user.is_human)
            msg.put()
            return msg
        return ''
