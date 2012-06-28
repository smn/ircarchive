import os
import logging
import base64

from urllib2 import quote
from datetime import datetime, timedelta

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import memcache

from django.utils import simplejson as json

from models import Message, Channel, User
from utils import prefetch_refprops


PAGE_SIZE = 20
DATE_FORMAT = '%Y%m%d%H%M%S'


class BaseHandler(webapp.RequestHandler):

    def render_to_string(self, template_file, context):
        path = os.path.join(os.path.dirname(__file__), template_file)
        return template.render(path, context)

    def render_to_response(self, template_file, context):
        return self.response.out.write(self.render_to_string(template_file,
            context))

    def redirect_to(self, location):
        self.response.set_status(301)
        self.response.headers['Location'] = location.encode('utf8')

    def challenge(self, realm):
        self.response.set_status(401, message='Authorization Required')
        self.response.headers['WWW-Authenticate'] = (
            'Basic realm="%s"' % realm).encode('utf8')

    def authenticate(self, realm, callback):
        auth = self.request.headers.get('Authorization')
        if auth:
            auth_parts = auth.split(' ')
            username, password = base64.b64decode(auth_parts[1]).split(':')
            if not callback(username, password):
                self.challenge(realm)
                return False
            return True
        else:
            self.challenge(realm)
            return False


class ArchiveHandler(BaseHandler):
    def get(self):
        self.render_to_response('templates/index.html', locals())

    def post(self):
        try:
            Message.log_common_message_format(self.request.body)
            self.response.set_status(201)
            self.response.headers['Content-Length'] = '0'
            self.response.out.write('')
        except (ValueError, KeyError, AttributeError), e:
            logging.error(e)
            self.response.set_status(400)
            self.response.headers['Content-Length'] = '0'
            self.response.out.write('')


class LogSweepHandler(BaseHandler):
    def get(self):
        messages = Message.all().filter('timestamp < ',
            datetime.utcnow() - timedelta(weeks=52))
        entries = messages.fetch(1000)
        db.delete(entries)
        for channel in Channel.all():
            messages = Message.all().filter('channel = ', channel)
            if not messages.get():
                db.delete(channel)


class BotFlaggingHandler(BaseHandler):
    """If a user's been active on ircarchive but is now flagged as being
    a bot then go back into history and mark their messages as such"""
    def get(self):
        bots = User.all().filter('is_human = ', False)
        for bot in bots:
            messages = Message.all().filter('user = ', bot).filter(
                'user_is_human = ', True).fetch(1000)
            for message in messages:
                message.user_is_human = False
            db.put(messages)

        humans = User.all().filter('is_human = ', True)
        for human in humans:
            messages = Message.all().filter('user = ', human)\
                            .filter('user_is_human = ', False).fetch(1000)
            for message in messages:
                message.user_is_human = True
            db.put(messages)


class ClearHandler(BaseHandler):
    def get(self):
        # for i in range(10):
        #     db.delete(Message.all().fetch(1000))
        #     db.delete(User.all().fetch(1000))
        #     db.delete(Channel.all().fetch(1000))
        pass


class BotHandler(BaseHandler):
    def post(self):
        payload = json.loads(self.request.body)
        nickname = payload.get('nickname')
        server = payload.get('server')
        is_human = payload.get('is_human')
        user = User.find(server, nickname)
        if user:
            user.is_human = bool(is_human)
            user.save()


class ChannelHandler(BaseHandler):

    def get(self, server, channel):
        channel = Channel.find(server, channel)

        if channel.is_private():
            if not self.authenticate('Private IRC channel %s' %
                channel.channel, channel.authenticate):
                return

        hide_bots = self.request.GET.get('hide_bots', '1') == '1'
        search_str = self.request.GET.get('q', '')
        query = Message.all().search(search_str,
            properties=['message_content']).filter('channel =', channel)

        if hide_bots:
            query = query.filter('user_is_human = ', True)

        query = query.order('-timestamp')

        cursor = self.request.GET.get('c')
        if cursor:
            query.with_cursor(cursor)
            previous = memcache.get(cursor) or ''

        today = datetime.utcnow().date()
        messages = query.fetch(PAGE_SIZE)
        next = query.cursor()
        if cursor:
            memcache.set(next, cursor)
        # optimization
        prefetch_refprops(messages, Message.user)
        notification = self.request.GET.get('msg')
        self.render_to_response('templates/channel.html', {
            'hide_bots': hide_bots,
            'channel': channel,
            'messages': messages,
            'notification': notification,
            'today': today,
            'next': next,
            'previous': previous,
        })


class EditChannelHandler(BaseHandler):

    def get(self, server, channel):
        channel = Channel.find(server, channel)
        if channel.is_private():
            if not self.authenticate('Private IRC chanenl %s' %
                channel.channel, channel.authenticate):
                return
        self.render_to_response('templates/edit_channel.html', locals())

    def post(self, server, channel):
        channel = Channel.find(server, channel)
        channel.username = self.request.POST.get('username')
        channel.password = self.request.POST.get('password')
        channel.save()
        msg = 'Channel properties have been updated'
        self.redirect_to('/channel/%s/%s/?msg=%s' % (channel.server,
            quote(channel.channel), msg))
