from google.appengine.ext import db
from google.appengine.ext.webapp import xmpp_handlers
from models import Message
import logging

"""
Sample json received via XMPP:

{
    "nickname": "sdehaan",
    "server": "irc.freenode.net",
    "channel": "#vumi",
    "message_type": "message",
    "message_content": "testing app engine",
    "timestamp": "2011-05-16T08:17:53.749184"
}

"""

class XmppHandler(xmpp_handlers.CommandHandler):
    def text_message(self, message=None):
        im_from = db.IM("xmpp", message.sender)
        
        # only accept from XMPP messages from our domain
        if '@praekeltfoundation.org' not in im_from.address:
            logging.info("Rejecting %s from %s" % (message.body, im_from.address))
            return
        
        msg = Message.log(message.body)
        logging.info('Wrote %s %s' % ("Message", msg.key()))
