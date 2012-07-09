import json
import os.path

from unittest import TestCase

from google.appengine.ext import testbed

from ircarchive.base.models import Message


class BaseTestCase(TestCase):

    fixtures = []

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        for fixture in self.fixtures:
            Message.log_common_message_format(fixture)

    def load_fixture(self, path):
        with open(os.path.join('fixtures', path), 'r') as fp:
            for message in json.load(fp):
                Message.log_common_message_format(message)

    def tearDown(self):
        self.testbed.deactivate()
