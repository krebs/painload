# jsb/plugs/common/forward.py
#
#

""" forward events occuring on a bot to another bot through xmpp. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.callbacks import callbacks, remote_callbacks, last_callbacks, first_callbacks
from jsb.lib.eventbase import EventBase
from jsb.lib.persist import PlugPersist
from jsb.utils.lazydict import LazyDict
from jsb.lib.examples import examples
from jsb.lib.fleet import getfleet
from jsb.lib.container import Container
from jsb.lib.errors import NoProperDigest
from jsb.utils.exception import handle_exception
from jsb.utils.locking import locked
from jsb.utils.generic import strippedtxt, stripcolor

## twitter plugin imports

from jsb.plugs.common.twitter import postmsg

## xmpp import

from jsb.contrib.xmlstream import NodeBuilder, XMLescape, XMLunescape

## basic imports

import logging
import copy
import time
import types
import hmac 
import hashlib

## defines

forward = PlugPersist("forward-core")
if not forward.data.allowin:
    forward.data.allowin = []
if not forward.data.channels:
    forward.data.channels = {}
if not forward.data.outs:
    forward.data.outs = {}
if not forward.data.whitelist:
    forward.data.whitelist = {}

cpy = copy.deepcopy

## forward-precondition

def forwardoutpre(bot, event):
    """ preconditon to check if forward callbacks is to be fired. """
    if event.how == "background": return False
    chan = unicode(event.channel).lower()
    if not chan: return
    logging.debug("forward - pre - %s" % event.channel)
    if chan in forward.data.channels and not event.isremote() and not event.forwarded:
        if event.how != u"background": return True
    return False

## forward-callback

def forwardoutcb(bot, event): 
    """ forward callback. """
    e = cpy(event)
    logging.debug("forward - cbtype is %s - %s" % (event.cbtype, event.how))
    e.forwarded = True
    e.source = bot.cfg.user
    e.botname = bot.cfg.server or bot.cfg.name
    if not event.chan: event.bind(bot)
    if event.chan: e.allowwatch = event.chan.data.allowwatch
    fleet = getfleet()
    for jid in forward.data.channels[event.channel.lower()]:
        if not "@" in jid: logging.error("forward - %s is not a valid JID" % jid) ; continue
        logging.info("forward - sending to %s" % jid)
        if jid == "twitter":
            try: postmsg(forward.data.outs[jid], e.txt)
            except Exception, ex: handle_exception()
            continue
        outbot = fleet.getfirstjabber(bot.isgae)
        if not outbot and bot.isgae: outbot = fleet.makebot('xmpp', 'forwardbot')
        if outbot:
            e.source = outbot.cfg.user
            txt = outbot.normalize(e.tojson())
            txt = stripcolor(txt)
            #txt = e.tojson()
            container = Container(outbot.cfg.user, txt)
            outbot.outnocb(jid, container.tojson()) 
        else: logging.info("forward - no xmpp bot found in fleet".upper())

first_callbacks.add('BLIP_SUBMITTED', forwardoutcb, forwardoutpre)
first_callbacks.add('MESSAGE', forwardoutcb, forwardoutpre)
#first_callbacks.add('PRESENCE', forwardoutcb, forwardoutpre)
first_callbacks.add('PRIVMSG', forwardoutcb, forwardoutpre)
first_callbacks.add('JOIN', forwardoutcb, forwardoutpre)
first_callbacks.add('PART', forwardoutcb, forwardoutpre)
first_callbacks.add('QUIT', forwardoutcb, forwardoutpre)
first_callbacks.add('NICK', forwardoutcb, forwardoutpre)
first_callbacks.add('CONSOLE', forwardoutcb, forwardoutpre)
first_callbacks.add('WEB', forwardoutcb, forwardoutpre)
first_callbacks.add('DISPATCH', forwardoutcb, forwardoutpre)
first_callbacks.add('OUTPUT', forwardoutcb, forwardoutpre)
first_callbacks.add('TORNADO', forwardoutcb, forwardoutpre)

## forward-add command

def handle_forwardadd(bot, event):
    """ arguments: <bot JID> - add a new forward (xmpp account). """
    if not event.rest:
        event.missing('<bot JID>')
        return
    if "@" in event.rest:
        forward.data.outs[event.rest] = event.user.data.name
        forward.save()
        if not event.rest in event.chan.data.forwards: event.chan.data.forwards.append(event.rest)
    else: event.reply("arguments must be a JID (Jabber ID).") ; return
    if event.rest:
        event.chan.save()
        event.done()

cmnds.add("forward-add", handle_forwardadd, 'OPER')
examples.add("forward-add" , "add a bot JID to forward to", "forward-add jsoncloud@appspot.com")

## forward-del command

def handle_forwarddel(bot, event):
    """ arguments: <bot JID> - delete a forward. """
    if not event.rest:
        event.missing('<bot JID>')
        return
    try: del forward.data.outs[event.rest]
    except KeyError: event.reply("no forward out called %s" % event.rest) ; return
    forward.save()
    if event.rest in event.chan.data.forwards: event.chan.data.forwards.remove(event.rest) ; event.chan.save()
    event.done()

cmnds.add("forward-del", handle_forwarddel, 'OPER')
examples.add("forward-del" , "delete an JID to forward to", "forward-del jsoncloud@appspot.com")

## forward-allow command

def handle_forwardallow(bot, event):
    """ arguments: <bot JID> - allow a remote bot to forward to us. """
    if not event.rest:
        event.missing("<bot JID>")
        return
    if forward.data.whitelist.has_key(event.rest):
        forward.data.whitelist[event.rest] = bot.type
        forward.save()
    event.done()

cmnds.add("forward-allow", handle_forwardallow, 'OPER')
examples.add("forward-allow" , "allow an JID to forward to us", "forward-allow jsonbot@jsonbot.org")

## forward-list command

def handle_forwardlist(bot, event):
    """ no arguments: list forwards of a channel. """
    try: event.reply("forwards for %s: " % event.channel, forward.data.channels[event.channel])
    except KeyError: event.reply("no forwards for %s" % event.channel)

cmnds.add("forward-list", handle_forwardlist, 'OPER')
examples.add("forward-list" , "list all forwards of a channel", "forward-list")

## forward command

def handle_forward(bot, event):
    """ arguments: <list of bot JIDs> - forward the channel tot other bots. """
    if not event.args:
        event.missing("<list of bot JIDs>")
        return
    forward.data.channels[event.channel.lower()] =  event.args
    for jid in event.args:
        forward.data.outs[jid] = event.user.data.name
        if not jid in event.chan.data.forwards: event.chan.data.forwards = event.args
    if event.args: event.chan.save()
    forward.save()
    event.done()

cmnds.add("forward", handle_forward, 'OPER')
examples.add("forward" , "forward a channel to provided JIDS", "forward jsoncloud@appspot.com")

## forward-stop command

def handle_forwardstop(bot, event):
    """ arguments: <list of bot JIDs> - stop forwarding the channel to other bots. """
    if not event.args:
        event.missing("<list of bot JIDs>")
        return

    try:
        for jid in event.args:
            try:
                forward.data.channels[event.channel].remove(jid)
                del forward.data.outs[jid]
                if jid in event.chan.data.forwards: event.chan.data.forwards.remove(jid)
            except ValueError: pass
        forward.save()
        event.done()
    except KeyError, ex: event.reply("we are not forwarding %s" %  str(ex))

cmnds.add("forward-stop", handle_forwardstop, 'OPER')
examples.add("forward-stop" , "stop forwarding a channel to provided JIDS", "forward-stop jsoncloud@appspot.com")
