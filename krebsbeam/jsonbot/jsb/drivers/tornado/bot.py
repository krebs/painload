# jsb/drivers/tornado/bot.py
#
#

""" tornado web bot. """

## jsb imports

from jsb.lib.botbase import BotBase
from jsb.lib.outputcache import add
from jsb.utils.generic import toenc, fromenc, strippedtxt, stripcolor
from jsb.utils.url import re_url_match
from jsb.utils.timeutils import hourmin
from jsb.lib.channelbase import ChannelBase
from jsb.imports import getjson
from jsb.lib.container import Container
from jsb.utils.exception import handle_exception
from jsb.lib.eventbase import EventBase
json = getjson()

## basic imports

import logging
import re
import cgi
import urllib
import time
import copy

## tornado import

import tornado.ioloop
import tornado.web

## defines

cpy = copy.deepcopy

## WebBot class

class TornadoBot(BotBase):

    """ TornadoBot  just inherits from botbase for now. """

    def __init__(self, cfg=None, users=None, plugs=None, botname="tornado-bot", *args, **kwargs):
        BotBase.__init__(self, cfg, users, plugs, botname, *args, **kwargs)
        assert self.cfg
        self.type = u"tornado"
        self.isgae = False
        self.websockets = {}

    def _raw(self, txt, target, how, handler, end=u"<br>"):
        """  put txt to the client. """
        if not txt: return 
        txt = txt + end
        handler.write(txt)
        logging.debug("%s - out - %s" % (self.cfg.name, txt))

    def outnocb(self, channel, txt, how=None, event=None, origin=None, response=None, dotime=False, *args, **kwargs):
        txt = self.normalize(txt)
        if event and event.how != "background":
            logging.info("%s - out - %s" % (self.cfg.name, txt))
        if "http://" in txt or "https://" in txt:
             for item in re_url_match.findall(txt):
                 logging.debug("web - raw - found url - %s" % item)
                 url = u'<a href="%s" onclick="window.open(\'%s\'); return false;">%s</a>' % (item, item, item)
                 try: txt = txt.replace(item, url)
                 except ValueError:  logging.error("web - invalid url - %s" % url)
        if response: self._raw(txt, event.target, event.how, event.handler)
        else:
            if event:
                e = cpy(event)
                e.txt = txt
                e.channel = channel
                e.how = event.how or how
            else:
                e = EventBase()
                e.nick = self.cfg.nick
                e.userhost = self.cfg.nick + "@" + "bot"
                e.channel = channel
                e.txt = txt
                e.div = "content_div"
                e.origin = origin
                e.how = how or "overwrite"
                e.headlines = True
            e.update(kwargs)
            update_web(self, e)
        self.benice(event)

    def normalize(self, txt):
        txt = stripcolor(txt)
        txt = txt.replace("\n", "<br>");
        txt = txt.replace("<", "&lt;")
        txt = txt.replace(">", "&gt;")
        txt = strippedtxt(txt)
        txt = txt.replace("&lt;br&gt;", "<br>")
        txt = txt.replace("&lt;b&gt;", "<b>")
        txt = txt.replace("&lt;/b&gt;", "</b>")
        txt = txt.replace("&lt;i&gt;", "<i>")
        txt = txt.replace("&lt;/i&gt;", "</i>")   
        txt = txt.replace("&lt;h2&gt;", "<h2>")
        txt = txt.replace("&lt;/h2&gt;", "</h2>")
        txt = txt.replace("&lt;h3&gt;", "<h3>")
        txt = txt.replace("&lt;/h3&gt;", "</h3>")
        txt = txt.replace("&lt;li&gt;", "<li>")
        txt = txt.replace("&lt;/li&gt;", "</li>")
        return txt

    def reconnect(self, *args): return True


def update_web(bot, event, end="<br>"):
        out = Container(event.userhost, event.tojson(), how="tornado").tojson()
        logging.info("%s - out - %s" % (bot.cfg.name, out))
        if not bot.websockets.has_key(event.channel): logging.info("no %s in websockets dict" % event.channel) ; return
        for c in bot.websockets[event.channel]:
            time.sleep(0.01)
            c.write_message(out)
