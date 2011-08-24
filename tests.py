from unittest import TestCase
from webtest import TestApp
from main import application
from models import Channel
from django.utils import simplejson as json

app = TestApp(application)

class BackboneTestCase(TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_output(self):
        channel1 = Channel(channel='#channel1', server="irc.server.net")
        channel1.save()
        
        channel2 = Channel(channel='#channel2', server="irc.server.net")
        channel2.save()
        
        channel3 = Channel(channel='channel3', server="irc.server.net")
        channel3.save()
        
        response = json.loads(app.get('/index.json').body)
        
        self.assertEquals(len(response), 2)
        self.assertTrue({
            'username': '',
            'password': '',
            'topic': None,
            'channel': '#channel1',
            'server': 'irc.server.net'
        } in response)