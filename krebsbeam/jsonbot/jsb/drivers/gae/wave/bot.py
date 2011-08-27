# jsb/wave/bot.py
#
#

""" google wave bot. """

## jsb imports

from jsb.lib.persist import Persist
from jsb.lib.botbase import BotBase
from jsb.lib.plugins import plugs
from jsb.version import getversion
from jsb.lib.callbacks import callbacks
from jsb.lib.outputcache import add
from jsb.lib.config import Config, getmainconfig
from jsb.utils.locking import lockdec
from jsb.utils.exception import handle_exception
from jsb.utils.generic import strippedtxt
from jsb.utils.trace import calledfrom
from jsb.lib.jsbimport import _import_byfile
from jsb.lib.datadir import getdatadir
import jsb.contrib.simplejson as simplejson

## gaelib imports

from jsb.utils.gae.auth import finduser
from event import WaveEvent
from waves import Wave

## waveapi v2 imports

from waveapi import events
from waveapi import robot
from waveapi import element
from waveapi import ops
from waveapi import blip
from waveapi import appengine_robot_runner

import waveapi

## generic imports

import logging
import cgi
import os
import time
import thread
import sys

## defines

saylock = thread.allocate_lock()
saylocked = lockdec(saylock)

## WaveBot claass

class WaveBot(BotBase, robot.Robot):

    """ bot to implement google wave stuff. """

    def __init__(self, cfg=None, users=None, plugs=None, name=None, domain=None,
                 image_url='http://jsonbot.appspot.com/assets/favicon.png',
                 profile_url='http://jsonbot.appspot.com/', *args, **kwargs):
        sname = 'jsb'
        BotBase.__init__(self, cfg, users, plugs, name, *args, **kwargs)
        assert self.cfg
        self.type = 'wave'
        if domain: self.cfg.domain = domain
        else: self.cfg.domain = getmainconfig().domain or "wave,google.com"
        self.cfg.nick = self.cfg.nick or name or "gae-wave"
        self.overload = True
        robot.Robot.__init__(self, name=getmainconfig().app_id or self.cfg.nick, image_url=image_url, profile_url=profile_url)
        credentials = _import_byfile("credentials", getdatadir() + os.sep + "config" + os.sep + "credentials.py")
        self.set_verification_token_info(credentials.verification_token[self.cfg.domain], credentials.verification_secret[self.cfg.domain])
        self.setup_oauth(credentials.Consumer_Key[self.cfg.domain], credentials.Consumer_Secret[self.cfg.domain],
                             server_rpc_base=credentials.RPC_BASE[self.cfg.domain])
        self.register_handler(events.BlipSubmitted, self.OnBlipSubmitted)
        self.register_handler(events.WaveletSelfAdded, self.OnSelfAdded)
        self.register_handler(events.WaveletParticipantsChanged, self.OnParticipantsChanged)
        self.iswave = True
        self.isgae = True
 
    def OnParticipantsChanged(self, event, wavelet):
        """ invoked when any participants have been added/removed. """
        wevent = WaveEvent()
        wevent.parse(self, event, wavelet)
        whitelist = wevent.chan.data.whitelist
        if not whitelist: whitelist = wevent.chan.data.whitelist = []
        participants = event.participants_added
        logging.warning("wave - %s - %s joined" % (wevent.chan.data.title, participants))
        if wevent.chan.data.protected:
            for target in participants:
                if target not in whitelist and target != 'jsb@appspot.com' and target != wevent.chan.data.owner:
                    logging.warn("wave - %s - setting %s to read-only" % (wevent.chan.data.title, target))
                    wevent.root.participants.set_role(target, waveapi.wavelet.Participants.ROLE_READ_ONLY)
        callbacks.check(self, wevent)

    def OnSelfAdded(self, event, wavelet):
        """ invoked when the robot has been added. """
        logging.warn('wave - joined "%s" (%s) wave' % (wavelet._wave_id, wavelet._title))
        wevent = WaveEvent()
        wevent.parse(self, event, wavelet)
        logging.debug("wave - owner is %s" % wevent.chan.data.owner)
        wevent.chan.data.json_data = wavelet.serialize()
        wevent.chan.save()
        wevent.reply("Welcome to %s (see !help) or http://jsonbot.appspot.com/docs/html/index.html" % getversion())
        callbacks.check(self, wevent)

    def OnBlipSubmitted(self, event, wavelet):
        """ new blip added. here is where the command dispatching takes place. """
        wevent = WaveEvent()
        wevent.parse(self, event, wavelet)
        wevent.auth = wevent.userhost
        wave = wevent.chan
        #wave.data.seenblips += 1
        wave.data.lastedited = time.time()
        self.doevent(wevent)

    def _raw(self, txt, event=None, *args, **kwargs):
        """ output some txt to the wave. """
        assert event.chan
        if not event.chan: logging.error("%s - event.chan is not set" % self.cfg.name) ; return
        if event.chan.data.json_data: wavelet = self.blind_wavelet(event.chan.data.json_data)
        else: logging.warn("did not join channel %s" % event.chan.data.id) ; return
        if not wavelet: logging.error("cant get wavelet") ; return
        txt = self.normalize(txt)
        txt = unicode(txt.strip())
        logging.warn("%s - wave - out - %s" % (self.cfg.name, txt))             
        try:
            annotations = []
            for url in txt.split():
                got = url.find("http://")
                if got != -1:
                    logging.debug("wave - found url - %s" % str(url))
                    start = txt.find(url.strip())
                    if url.endswith(">"): annotations.append((start+2, start+len(url)-1, "link/manual", url[1:-1]))
                    else: annotations.append((start, start+len(url), "link/manual", url))
        except Exception, ex: handle_exception()
        logging.debug("annotations used: %s", annotations)
        reply = wavelet.reply(txt)
        if annotations:
            for ann in annotations:
                if ann[0]:
                    try: reply.range(ann[0], ann[1]).annotate(ann[2], ann[3])
                    except Exception, ex: handle_exception()
        logging.info("submitting to server: %s" % wavelet.serialize())
        try:
            import google
            self.submit(wavelet)
        except google.appengine.api.urlfetch_errors.DownloadError: handle_exception()

    def outnocb(self, waveid, txt, result=[], event=None, origin="", dot=", ", *args, **kwargs):
        """ output to the root id. """
        if not self._server_rpc_base or not (self.cfg.domain in self._server_rpc_base):
            credentials = _import_byfile("credentials", getdatadir() + os.sep + "config" + os.sep + "credentials.py")
            rpc_base = credentials.RPC_BASE[waveid.split("!")[0]]
            self._server_rpc_base = rpc_base
            logging.warn("%s - %s - server_rpc_base is %s" % (self.cfg.name, waveid, self._server_rpc_base))
        if not event: logging.error("wave - event not set - %s" % calledfrom(sys._getframe(0)))
        logging.warn("wave - creating new event.")
        wave = Wave(waveid)
        wave.say(self, txt)

    def toppost(self, waveid, txt):
        """ output to the root id. """
        if not self.cfg.domain in waveid:
            logging.warn("%s - not connected - %s" % (self.cfg.name, waveid))
            return
        wave = Wave(waveid)
        if wave and wave.data.waveid: wave.toppost(self, txt)
        else: logging.warn("%s - we are not joined to %s" % (self.cfg.name, waveid))

    def newwave(self, domain=None, participants=None, submit=False):
        """ create a new wave. """
        logging.info("wave - new wave on domain %s" % domain)
        newwave = self.new_wave(domain or self.cfg.domain, participants=participants, submit=submit)
        return newwave

    def run(self):
        """ start the bot on the runner. """
        appengine_robot_runner.run(self, debug=True, extra_handlers=[])

    def normalize(self, what):
        """ convert markup to IRC bold. """
        txt = strippedtxt(what)
        txt = txt.replace("<b>", "")
        txt = txt.replace("</b>", "")
        txt = txt.replace("<i>", "")
        txt = txt.replace("</i>", "")
        txt = txt.replace("&lt;b&gt;", "")
        txt = txt.replace("&lt;/b&gt;", "")
        txt = txt.replace("&lt;i&gt;", "")
        txt = txt.replace("&lt;/i&gt;", "")
        txt = txt.replace("&lt;h2&gt;", "")
        txt = txt.replace("&lt;/h2&gt;", "")
        txt = txt.replace("&lt;h3&gt;", "")
        txt = txt.replace("&lt;/h3&gt;", "")
        txt = txt.replace("&lt;li&gt;", "")
        txt = txt.replace("&lt;/li&gt;", "")
        return txt
