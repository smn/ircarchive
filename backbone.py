from google.appengine.ext import webapp
from models import Channel
from urllib2 import quote
from django.utils import simplejson as json

class JSONHandler(webapp.RequestHandler):

    CONTENT_TYPE = 'application/json; charset=utf-8'

    def render_json_list(self, models):
        self.response.headers['Content-Type'] = self.CONTENT_TYPE
        self.response.out.write(json.dumps([m.to_dict() for m in models]))

    def render_json(self, model):
        self.response.headers['Content-Type'] = self.CONTENT_TYPE
        self.response.out.write(json.dumps(model.to_dict()))

class IndexHandler(JSONHandler):
    def get(self):
        self.render_json_list(Channel.list())


class ChannelHandler(JSONHandler):
    def get(self):
        server_name = self.request.GET.get('server', '')
        channel_name = self.request.GET.get('channel', '')
        channel = Channel.find(server_name, channel_name)
        self.render_json(channel)
