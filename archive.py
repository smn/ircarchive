from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import memcache
from models import Message, Channel
from utils import prefetch_refprops, key
from django.core.paginator import Paginator, EmptyPage, InvalidPage
import os, logging
from datetime import datetime, timedelta

PAGE_SIZE=200
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

class ChannelHandler(BaseHandler):
    
    def get(self, server, channel):
        channel = Channel.find(server, channel)
        query = Message.all().filter('channel =', channel) \
                                        .order('-timestamp')
        last_cursor = self.request.GET.get('c')
        if last_cursor:
            query.with_cursor(last_cursor)
        
        try:
            previous = query.cursor()
        except AssertionError:
            # we're at the start
            previous = None
        messages = query.fetch(PAGE_SIZE)
        next = query.cursor()
        self.render_to_response('templates/channel.html', locals())
        