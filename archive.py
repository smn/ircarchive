from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import memcache
from models import Message, Channel, User, Tag
from utils import prefetch_refprops, key
import os, logging, json
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
        messages = Message.all().filter('timestamp < ', datetime.utcnow() - timedelta(weeks=2))
        self.response.out.write('Deleting: %s <br/>' % messages.count())
        entries = messages.fetch(1000)
        db.delete(entries)
        for channel in Channel.all():
            messages = Message.all().filter('channel = ', channel)
            if not messages.get():
                self.response.out.write('Deleting channel: %s <br/>' % channel.channel)
                db.delete(channel)

class TagHandler(BaseHandler):
    def post(self):
        payload = json.loads(self.request.body)
        nickname = payload.get('nickname')
        server = payload.get('server')
        tags = Tag.get_or_create(*payload.get('tags', []))
        user = User.find(server, nickname)
        if user:
            user.tags = [tag.key() for tag in tags]
            user.save()
    

class ChannelHandler(BaseHandler):
    
    def get(self, server, channel):
        channel = Channel.find(server, channel)
        
        all_tags = Tag.all()
        hide_tag_names = self.request.get_all('hide_tag')
        hide_tags = [tag for tag in all_tags if tag.name in hide_tag_names]
        
        query = Message.all().filter('channel =', channel)
        if hide_tags:
            for selected_tag in selected_tags:
                query = query.filter('tags != ', selected_tag)
        
        query = query.order('-timestamp')
        
        # hide_keys = list(hide_keys)
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
        