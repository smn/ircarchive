from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import memcache
from models import Message, Channel
from utils import prefetch_refprops, key
from urllib2 import unquote
import os, logging

def render(template_file, context):
    path = os.path.join(os.path.dirname(__file__), template_file)
    return template.render(path, context)

class ArchiveHandler(webapp.RequestHandler):
    def get(self):
        channels = [channel for channel in Channel.all() 
                        if channel.channel.startswith('#')]
        self.response.out.write(render('templates/index.html', locals()))
    
    def post(self):
        msg = Message.log(self.request.body)
        self.response.set_status(201)
        self.response.out.write(msg.key())

class ChannelHandler(webapp.RequestHandler):
    def get(self, server, channel):
        key = db.Key.from_path(Channel.kind(), '%s/%s' % (unquote(channel), server))
        channel = Channel.get(key)
        messages = Message.all().filter('channel =', channel).order('-timestamp')
        self.response.out.write(render('templates/channel.html', locals()))
        