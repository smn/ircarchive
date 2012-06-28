from datetime import datetime
from unittest import TestCase

from google.appengine.ext import testbed

from models import Message


class MessageModelTestCase(TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.sample_msg = """{
            "transport_name": "irc",
            "in_reply_to": null,
            "from_addr": "user1",
            "timestamp": "2012-01-03 11:29:57.0",
            "to_addr": "#channel",
            "content": "user2: Woot. I'll restart vumibot.",
            "message_version": "20110921",
            "transport_type": "irc",
            "transport_metadata": {},
            "helper_metadata": {
                "irc": {
                    "transport_nickname": "vumibot",
                    "irc_addressed_to_transport": false,
                    "irc_full_sender": "user1!~client@somedomain.net",
                    "irc_command": "PRIVMSG",
                    "irc_full_recipient": "#channel",
                    "irc_channel": "#channel",
                    "irc_server": "irc.freenode.net:6667"
                }
            },
            "session_event": null,
            "message_id": "19d41fbd03224eef85eb29c6c97ee28b",
            "message_type": "user_message"
        }"""

    def tearDown(self):
        self.testbed.deactivate()

    def test_parse_timestamp(self):
        msg = Message.log_common_message_format(self.sample_msg)
        self.assertEqual(msg.timestamp, datetime(2012, 1, 3, 11, 29, 57))
