# jsb/wave/waves.py
#
#

""" class to repesent a wave. """

## jsb imports

from jsb.lib.channelbase import ChannelBase
from jsb.utils.exception import handle_exception
from jsb.utils.locking import lockdec
from jsb.utils.generic import strippedtxt, toenc, fromenc

## basic imports

import logging
import copy
import os
import time
import re
import thread

## defines

findurl = re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]")
cpy = copy.deepcopy

saylock = thread.allocate_lock()
saylocked = lockdec(saylock)

## Wave class (channel)

class Wave(ChannelBase):

    """ a wave is seen as a channel. """

    def __init__(self, waveid, botname=None):
        ChannelBase.__init__(self, waveid, botname)
        self.data.seenblips = self.data.seenblips or 0
        self.data.threshold = self.data.threshold or -1
        self.data.nrcloned = self.data.nrcloned or 0
        self.data.waveid = waveid
        self.wavelet = None
        self.event = None
        logging.debug("created wave with id: %s" % waveid)

    def parse(self, event, wavelet):
        """ parse event into a Wave. """
        self.data.json_data = wavelet.serialize()
        self.data.title = wavelet._title
        self.data.waveletid = wavelet._wavelet_id
        self.wavelet = wavelet
        self.event = event
        logging.debug("parsed %s (%s) channel" % (self.data.waveid, self.data.title))
        return self

    def set_title(self, title, cloned=False):
        """ set title of wave. """
        self.event.set_title(title, cloned)

    def clone(self, bot, event, title=None, report=False, participants=[]):
        """ clone the wave into a new one. """
        if participants: parts = participants
        else: parts = list(event.root.participants)
        newwave = bot.newwave(event.domain, parts)
        logging.info("wave - clone - populating wave with %s" % str(parts))
        for id in parts: newwave.participants.add(id)
        if title:
            if '#' in title:
                title = "#".join(title.split("#")[:-1])
                title += "#%s" % str(self.data.nrcloned + 1)
            else: title += " - #%s" % str(self.data.nrcloned + 1)
            newwave._set_title(title)
        if report:
            try: txt = '\n'.join(event.rootblip.text.split('\n')[2:])
            except IndexError: txt = event.rootblip.text
            newwave._root_blip.append(u'%s\n' % txt)
            for element in event.rootblip.elements:
                if element.type == 'GADGET': newwave._root_blip.append(element)
            blip = newwave.reply()
            blip.append("\nthis wave is cloned from %s\n" % event.url)
        else: newwave._root_blip.append("PROTECTED WAVE")
        wavelist = bot.submit(newwave)
        logging.info("wave - clone - %s - submit returned %s" % (list(newwave.participants), str(wavelist)))
        if not wavelist:
            logging.warn("submit of new wave failed")
            return
        try:
            waveid = None
            for item in wavelist:
                try: waveid = item['data']['waveId']
                except (KeyError, ValueError): continue
            logging.info("wave - newwave id is %s" % waveid)
            if not waveid:
                logging.error("can't extract waveid from submit data")
                return
            if waveid and 'sandbox' in waveid:
                url = "https://wave.google.com/a/wavesandbox.com/#restored:wave:%s" % waveid.replace('w+','w%252B')
            else:
                url = "https://wave.google.com/wave/#restored:wave:%s" % waveid.replace('w+','w%252B')
            oldwave = Wave(event.waveid)
            oldwave.data.threshold = -1
            oldwave.save()
            wave = Wave(waveid)
            wave.parse(event, newwave)
            wave.data.json_data = newwave.serialize()
            wave.data.threshold = self.data.threshold or 200
            wave.data.nrcloned = self.data.nrcloned + 1
            wave.data.url = url
            wave.save()
        except Exception, ex:
            handle_exception()
            return
        return wave

    @saylocked
    def say(self, bot, txt):
        """ output some txt to the wave. """
        if self.data.json_data: wavelet = bot.blind_wavelet(self.data.json_data)
        else:
            logging.info("did not join channel %s" % self.id)
            return
        if not wavelet:
            logging.error("cant get wavelet")
            return
        txt = bot.normalize(txt)
        txt = unicode(txt.strip())
        logging.debug(u'wave - out - %s - %s' % (self.data.title, txt))
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
            bot.submit(wavelet)
        except google.appengine.api.urlfetch_errors.DownloadError: handle_exception()
        self.data.seenblips += 1
        self.data.lastedited = time.time()
        #self.save()

    saynocb = say

    def toppost(self, bot, txt):
        """ toppost some txt to the wave. """
        if self.data.json_data:
            logging.debug("wave - say - using BLIND - %s" % self.data.json_data) 
            wavelet = bot.blind_wavelet(self.data.json_data)
        else:
            logging.info("did not join channel %s" % self.id)
            return
        if not wavelet:
            logging.error("cant get wavelet")
            return
        logging.debug('wave - out - %s - %s' % (self.data.title, txt))
        try:
            import google
            blip = wavelet._root_blip.reply()
            blip.append(txt)
            bot.submit(wavelet)
        except google.appengine.api.urlfetch_errors.DownloadError: handle_exception()
        self.data.seenblips += 1
        self.data.lastedited = time.time()
        self.save()
