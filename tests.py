from django.utils import simplejson as json
from google.appengine.ext import testbed
from google.appengine.ext import db
from unittest import TestCase
from webtest import TestApp
from urllib2 import unquote

from main import application
from models import Channel

app = TestApp(application)

def request(method, path, *args, **kwargs):
    fn = getattr(app, method)
    return json.loads(fn(path, *args, **kwargs).body)

def create_channels(*names):
    channels = []
    for name in names:
        channel = Channel(channel=name, server='irc.server.net')
        channel.save()
        channels.append(channel)
    return channels
    

class BackboneTestCase(TestCase):
    
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        
        self.channels = create_channels('#channel1', '#channel2', 'channel3')
    
    def tearDown(self):
        self.testbed.deactivate()
    
    def test_channel_list(self):
        self.assertEquals(Channel.all().count(), 3)
        self.assertEquals(len(Channel.list()), 2)
        self.assertEquals(len(Channel.list(prefix='#')), 2)
        self.assertEquals(len(Channel.list(prefix=None)), 3)
    
    def test_index(self):
        self.assertEquals(Channel.all().count(), 3)
        response = request('get', '/index.json')
        self.assertEquals(len(response), 2)
        self.assertTrue({
            'username': '',
            'password': '',
            'topic': None,
            'channel': '#channel1',
            'server': 'irc.server.net'
        } in response)
    
    def test_channel(self):
        server = 'irc.server.net'
        channel = '#channel1'
        key = db.Key.from_path(Channel.kind(), '%s/%s' % (unquote(channel), server))
        print key
        print request('get', '/channel.json', {
            'server': 'irc.server.net',
            'channel': '#channel1'
        })