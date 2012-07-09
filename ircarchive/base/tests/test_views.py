print 'hi'
from ircarchive.base.tests.base import BaseTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse


class HomeTestCase(BaseTestCase):

    fixtures = ['sample.json']

    def test_homepage_rendering(self):
        print 'hello'
        client = Client()
        response = client.get(reverse('index'))
        self.assertTrue('#chanel' in response.content)
