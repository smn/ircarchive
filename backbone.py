from google.appengine.ext import webapp
from models import Channel
from django.utils import simplejson as json

class JSONHandler(webapp.RequestHandler):
    
    CONTENT_TYPE = 'application/json; charset=utf-8'
    
    def render_json(self, models):
        self.response.headers['Content-Type'] = self.CONTENT_TYPE
        self.response.out.write(json.dumps([m.to_dict() for m in models]))

class Index(JSONHandler):
    
    def get(self):
        self.render_json(Channel.list())
    
