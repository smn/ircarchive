from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from models import Message, Channel
import os

class ArchiveHandler(webapp.RequestHandler):
    def get(self):
        channel_names = [channel.channel for channel in Channel.all()
                            if channel.channel.startswith('#')]
        messages = Message.all().order('-timestamp').fetch(1000)
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, locals()))
