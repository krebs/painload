# jsb/gae/wave/event.py
#
#

""" google wave events. """

## jsb imports

from jsb.lib.eventbase import EventBase
from jsb.utils.exception import handle_exception
from jsb.utils.gae.auth import finduser
from jsb.drivers.gae.wave.waves import Wave


## basic imports

import logging
import cgi
import re
import time

## defines

findurl = re.compile(u"(http://.*)?")

## WaveEventclass

class WaveEvent(EventBase):

    """ a wave event. """

    def __init__(self):
        EventBase.__init__(self)
        self.bottype = "wave"
        self.msg = False
        self.target = None
        self.roottarget = None
        self.rootreply = None
        self.gadget = None
        self.result = []
        self.cbtype = "BLIP_SUBMITTED"
        self.overload = True

    def parse(self, bot, event, wavelet):
        """ parse properties and context into a WaveEvent. """
        self.bot = bot
        self.eventin = event
        self.wavelet = wavelet
        self.waveid = self.wavelet._wave_id
        self.blipid = self.eventin.blip_id
        self.blip = self.eventin.blip
        if not self.blip:
            logging.warn("can't get blip id: %s" % self.blipid)
            self.contributors = []
            self.txt = ""
            self.usercmnd = ""
            self.userhost = ""
            self.ispoller = False
        else:
            self.contributors = self.blip._contributors
            self.origtxt = self.blip._content.strip()
            self.txt = self.origtxt
            if len(self.txt) >= 2: self.usercmnd = self.txt[1:].split()[0]
            else: self.usercmnd = None
            self.userhost = self.blip._creator
            self.elements = self.blip._elements
            for nr, elem in self.elements.iteritems():
                logging.debug("wave - element - %s - %s" % (str(elem), dir(elem)))
                if elem.get('ispoller') == 'yes': self.ispoller = True
                if elem.get('gadgetcmnd') == 'yes':
                    self.cbtype = "DISPATCH"
                    logging.debug("wave.event - dispatch - %s" % str(elem))
                    self.txt = u"!" + elem.get("cmnd")
                    self.channel = self.waveid = elem.get("waveid")
                    self.gadgetnr = nr
                    self.cmndhow = elem.get('how')
                    self.userhost = elem.get('who')
        self.auth = self.userhost
        self.nick = self.userhost.split("@")[0]
        logging.debug("wave - event - auth is %s" % self.auth)
        self.root = wavelet
        self.rootblipid = wavelet._root_blip.blip_id
        self.rootblip = wavelet._root_blip
        self.raw_data = self.root._raw_data
        self.domain = self.wavelet.domain
        self.channel = self.waveid
        self.origin = self.channel
        self.title = self.root._title or self.channel 
        self.cmnd = self.cbtype = event.type
        if 'sandbox' in self.waveid:
            self.url = "https://wave.google.com/a/wavesandbox.com/#restored:wave:%s" % self.waveid.replace('w+','w%252B')
        else:
            self.url = "https://wave.google.com/wave/#restored:wave:%s" % self.waveid.replace('w+','w%252B')
        #self.chan = Wave(self.waveid)
        #self.chan.parse(self.eventin, self.wavelet)
        self.bind(self.bot, chan=Wave(self.channel))
        self.makeargs()        
        logging.debug(u'wave - in - %s - %s - %s' % (self.title, self.userhost, self.txt))

    def __deepcopy__(self, a):
        """ deepcopy a wave event. """
        e = WaveEvent()
        e.copyin(self)
        return e

    def toppost(self, txt):
        """ append to rootblip. """
        reply = self.rootblip.reply()
        reply.append(txt)
        if self.chan:
            self.chan.data.seenblips += 1
            self.chan.data.lastedited = time.time()
        return reply

    def insert_root(self, item):
        """ insert item in rootblip. """
        reply = self.rootblip.append(item)
        if self.chan:
            self.chan.data.seenblips += 1
            self.chan.data.lastedited = time.time()
        return self

    def set_title(self, title, cloned=False):
        """ set title of wave. """
        if cloned and self.chan and self.chan.data.nrcloned:
            title = "#".join(title.split("#")[:-1])
            title += "#%s" % str(self.chan.data.nrcloned)
        logging.info("wave - setting title - %s" % title)
        self.root._set_title(title)
        return self

    def append(self, item, annotations=None):
        """ append to new blip, or one if already created. use annotations if provided. """
        if not self.target and self.blip: self.target = self.blip.reply()
        self.result.append(item)
        try: self.target.append(item)
        except Exception, ex: handle_exception()
        logging.debug("wave - append - annotations are %s" % str(annotations))
        if annotations:
            for ann in annotations:
                if ann[0]:
                    try: self.target.range(ann[0], ann[1]).annotate(ann[2], ann[3])
                    except Exception, ex: handle_exception()
        if self.chan:
            self.chan.data.seenblips += 1
            self.chan.data.lastedited = time.time()
        return self

    def append_root(self, item , annotations=None):
        """ append to rootblip. use annotations if provided. """
        if not self.roottarget: self.roottarget = self.rootblip.reply()
        self.roottarget.append(item)
        self.result.append(item)
        if self.chan:
            self.chan.data.seenblips += 1
            self.chan.data.lastedited = time.time()
        return self.roottarget

    def appendtopper(self, item):
        """ top post. """
        self.rootblip.append(item)
        self.result.append(item)
        if self.chan:
            self.chan.data.seenblips += 1
            self.chan.data.lastedited = time.time()
        return self.rootblip

    def replyroot(self, txt, resultlist=[], event=None, origin="", dot=", ", *args, **kwargs):
        """ reply to wave root. """
        if self.checkqueues(resultlist): return
        outtxt = self.makeresponse(txt, resultlist, dot, *args, **kwargs)
        if not outtxt: return
        self.result.append(outtxt)
        (res1, res2) = self.less(outtxt)
        self.write_root(res1)

    def write_root(self, outtxt, end="\n", root=None):
        """ write to the root of a wave. """
        self.append_root(outtxt + end)
        self.replied = True
        self.bot.outmonitor(self.origin, self.channel, outtxt, self)

    def submit(self):
        """ submit event to the bot. """
        self.bot.submit(self.wavelet)
