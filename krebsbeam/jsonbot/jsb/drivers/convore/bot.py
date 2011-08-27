# jsb/lib/convore/bot.py
#
#

""" convore bot. """

## jsb import

from jsb.lib.botbase import BotBase
from jsb.lib.errors import NotConnected
from jsb.drivers.convore.event import ConvoreEvent
from jsb.utils.lazydict import LazyDict
from jsb.utils.exception import handle_exception
from jsb.imports import getjson, getrequests

## basic imports

import logging
import time
import urllib2

## defines

json = getjson()
requests = getrequests()

## ConvoreBot

class ConvoreBot(BotBase):

    """ The Convore Bot. """

    def __init__(self, cfg=None, usersin=None, plugs=None, botname=None, nick=None, *args, **kwargs):
        BotBase.__init__(self, cfg, usersin, plugs, botname, nick, *args, **kwargs)
        self.type = "convore"
        self.cursor = None
        if not self.state.has_key("namecache"): self.state["namecache"] = {}
        if not self.state.has_key("idcache"): self.state["idcache"] = {}
        self.cfg.nick = cfg.username or "jsonbot"

    def post(self, endpoint, data=None):
        logging.debug("%s - doing post on %s - %s" % (self.cfg.name, endpoint, data)) 
        assert self.cfg.username
        assert self.cfg.password
        self.auth = requests.AuthObject(self.cfg.username, self.cfg.password)
        res = requests.post("https://convore.com/api/%s" % endpoint, data or {}, auth=self.auth)
        logging.debug("%s - got result %s" % (self.cfg.name, res.content))
        if res.status_code == 200:
            logging.debug("%s - got result %s" % (self.cfg.name, res.content))
            return LazyDict(json.loads(res.content))
        else: logging.error("%s - %s - %s returned code %s" % (self.cfg.name, endpoint, data, res.status_code))

    def get(self, endpoint, data={}):
        logging.debug("%s - doing get on %s - %s" % (self.cfg.name, endpoint, data)) 
        self.auth = requests.AuthObject(self.cfg.username, self.cfg.password)
        url = "https://convore.com/api/%s" % endpoint
        res = requests.get(url, data, auth=self.auth)
        if res.status_code == 200:
            logging.debug("%s - got result %s" % (self.cfg.name, res.content))
            return LazyDict(json.loads(res.content))
        logging.error("%s - %s - %s returned code %s" % (self.cfg.name, endpoint, data, res.status_code))

    def connect(self):
        logging.warn("%s - authing %s" % (self.cfg.name, self.cfg.username))
        r = self.get('account/verify.json')
        if r: logging.warn("%s - connected" % self.cfg.name) ; self.connectok.set()
        else: logging.warn("%s - auth failed - %s" % (self.cfg.name, r)) ; raise NotConnected(self.cfg.username)

    def outnocb(self, printto, txt, how="msg", event=None, origin=None, html=False, *args, **kwargs):
        if event and not event.chan.data.enable:
            logging.warn("%s - channel %s is not enabled" % (self.cfg.name, event.chan.data.id))
            return
        txt = self.normalize(txt)
        logging.debug("%s - out - %s - %s" % (self.cfg.name, printto, txt))
        if event and event.msg:
            r = self.post("messages/%s/create.json" % printto, data={"message": txt, "pasted": True})
        else:
            r = self.post("topics/%s/messages/create.json" % printto, data={"message": txt, "pasted": True})

    def discover(self, channel):
        res = self.get("groups/discover/search.json", {"q": channel })
        logging.debug("%s - discover result: %s" % (self.cfg.name, str(res)))
        for g in res.groups:
            group = LazyDict(g)
            self.state["namecache"][group.id] = group.name
            self.state["idcache"][group.name] = group.id
        self.state.save()
        return res.groups

    def join(self, channel, password=None):
        if channel not in self.state['joinedchannels']: self.state['joinedchannels'].append(channel) ; self.state.save()
        try: 
            self.join_id(self.state["idcache"][channel])
        except KeyError:  
            chans = self.discover(channel)
            self.join_id(chans[0]["id"], password)

    def join_id(self, id, password=None):
        logging.warn("%s - joining %s" % (self.cfg.name, id))
        res = self.post("groups/%s/join.json" % id, {"group_id": id})
        return res

    def part(self, channel):
        logging.warn("%s - leaving %s" % (self.cfg.name, channel))
        try:
            id = self.state["idcache"][channel]
            res = self.post("groups/%s/leave.json" % id, {"group_id": id})
        except: handle_exception() ; return
        if channel in self.state['joinedchannels']: self.state['joinedchannels'].remove(channel) ; self.state.save()
        return res

    def _readloop(self):
        logging.debug("%s - starting readloop" % self.cfg.name)
        self.connectok.wait(15)
        self.auth = requests.AuthObject(self.cfg.username, self.cfg.password)
        while not self.stopped and not self.stopreadloop:
            try:
                time.sleep(1)
                if self.cursor: result = self.get("live.json", {"cursor": self.cursor})
                else: result = self.get("live.json")
                if self.stopped or self.stopreadloop: break
                if not result: time.sleep(20) ; continue
                if result.has_key("_id"): self.cursor = result["_id"]
                if not result: continue
                if not result.messages: continue
                logging.info("%s - incoming - %s" % (self.cfg.name, str(result)))
                for message in result.messages:
                    try:
                        event = ConvoreEvent()
                        event.parse(self, message, result)
                        if event.username.lower() == self.cfg.username.lower(): continue
                        event.bind(self)
                        method = getattr(self, "handle_%s" % event.type)
                        method(event)
                    except (TypeError, AttributeError): logging.error("%s - no handler for %s kind" % (self.cfg.name, message['kind'])) 
                    except: handle_exception()
            except urllib2.URLError, ex: logging.error("%s - url error - %s" % (self.cfg.name, str(ex)))
            except Exception, ex: handle_exception()
        logging.debug("%s - stopping readloop" % self.cfg.name)

    def handle_error(self, event):
        logging.error("%s - error - %s" % (self.cfg.name, event.error))

    def handle_logout(self, event):
        logging.info("%s - logout - %s" % (self.cfg.name, event.username))

    def handle_login(self, event):
        logging.info("%s - login - %s" % (self.cfg.name, event.username))

    def handle_star(self, event):
        pass
        #logging.warn("%s - star - %s" % (self.cfg.name, str(message)))

    def handle_topic(self, event):
        logging.info("%s - topic - %s" % (self.cfg.name, event.dump()))

    def handle_message(self, event):
        self.doevent(event)

    def handle_direct_message(self, event):
        self.doevent(event)
 