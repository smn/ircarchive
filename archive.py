from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import memcache
from models import Message, Channel, User
from utils import prefetch_refprops, key
from django.utils import simplejson as json
import os, logging, base64
from datetime import datetime, timedelta

PAGE_SIZE=20
DATE_FORMAT = '%Y%m%d%H%M%S'

class BaseHandler(webapp.RequestHandler):
    
    def render_to_string(self, template_file, context):
        path = os.path.join(os.path.dirname(__file__), template_file)
        return template.render(path, context)
    
    def render_to_response(self, template_file, context):
        return self.response.out.write(self.render_to_string(template_file, context))

class ArchiveHandler(BaseHandler):
    def get(self):
        channels = [channel for channel in Channel.all().order('channel') 
                        if channel.channel.startswith('#')]
        self.render_to_response('templates/index.html', locals())
    
    def post(self):
        msg = Message.log(self.request.body)
        self.response.set_status(201)
        self.response.out.write(msg.key())

class LogSweepHandler(BaseHandler):
    def get(self):
        messages = Message.all().filter('timestamp < ', datetime.utcnow() - timedelta(weeks=4))
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
        logging.info(bots)
        for bot in bots:
            messages = Message.all().filter('user = ',bot)\
                            .filter('user_is_human = ', True).fetch(1000)
            logging.info(messages)
            for message in messages:
                message.user_is_human = False
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
    
    def challenge(self, realm):
        self.response.set_status(401, message='Authorization Required')
        self.response.headers['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    
    def get(self, server, channel):
        channel = Channel.find(server, channel)
        
        if channel.is_private():
            auth = self.request.headers.get('Authorization')
            if auth:
                auth_parts = auth.split(' ')
                username, password = base64.b64decode(auth_parts[1]).split(':')
                if not channel.authenticate(username, password):
                    return self.challenge('Private IRC Channel %s' % channel.channel)
            else:
                return self.challenge('Private IRC Channel %s' % channel.channel)
        
        hide_bots = self.request.GET.get('hide_bots', '1') == '1'
        
        query = Message.all().filter('channel =', channel)
        
        if hide_bots:
            query = query.filter('user_is_human = ', True)
        
        quer = query.order('-timestamp')
        
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
        self.render_to_response('templates/channel.html', locals())
        