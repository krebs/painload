# jsb/gae/xmpp/bot.py
#
#

""" XMPP bot. """

## jsb imports

from jsb.lib.botbase import BotBase
from jsb.drivers.xmpp.presence import Presence
from jsb.utils.generic import strippedtxt

## xmpp import

from jsb.contrib.xmlstream import NodeBuilder, XMLescape, XMLunescape

## basic imports

import types
import logging

## XMPPBot class

class XMPPBot(BotBase):

    """ XMPPBot just inherits from BotBase for now. """

    def __init__(self, cfg=None, users=None, plugs=None, botname="gae-xmpp", *args, **kwargs):
        BotBase.__init__(self, cfg, users, plugs, botname, *args, **kwargs)
        assert self.cfg
        self.isgae = True
        self.type = "xmpp"

    def out(self, jids, txt, how="msg", event=None, origin=None, groupchat=None, *args, **kwargs):
        """ output xmpp message. """
        if type(jids) != types.ListType: jids = [jids, ]
        self.outnocb(jids, txt, how, event, origin)
        for jid in jids:
            self.outmonitor(self.cfg.nick, jid, txt)

    def outnocb(self, jids, txt, how="msg", event=None, origin=None, from_jid=None, message_type=None, raw_xml=False, groupchat=False, *args, **kwargs):
        """ output xmpp message. """
        from google.appengine.api import xmpp
        if not message_type: message_type = xmpp.MESSAGE_TYPE_CHAT
        if type(jids) != types.ListType: jids = [jids, ]
        txt = self.normalize(txt)
        logging.info(u"%s - xmpp - out - %s - %s" % (self.cfg.name, unicode(jids), txt))             
        xmpp.send_message(jids, txt, from_jid=from_jid, message_type=message_type, raw_xml=raw_xml)

    def invite(self, jid):
        """ send an invite to another jabber user. """
        from google.appengine.api import xmpp
        xmpp.send_invite(jid)

    def normalize(self, what):
        """ remove markup code as its not yet supported by our GAE XMPP bot. """
        what = strippedtxt(unicode(what))
        what = what.replace("<b>", "")
        what = what.replace("</b>", "")
        what = what.replace("&lt;b&gt;", "")
        what = what.replace("&lt;/b&gt;", "")
        what = what.replace("<i>", "")
        what = what.replace("</i>", "")
        what = what.replace("&lt;i&gt;", "")
        what = what.replace("&lt;/i&gt;", "")
        return what
