# jsb/plugs/common/feedback.py
#
#

""" give feedback on the bot to bthate@gmail.com. needs a xmpp server, so use jsb-xmpp or jsb-fleet. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.fleet import getfleet
from jsb.lib.factory import bot_factory
from jsb.utils.lazydict import LazyDict
from jsb.utils.generic import waitforqueue

## basic imports

import uuid
import time

## feedback command

def handle_feedback(bot, event):
    """ 
        arguments: <feedbacktxt> - give feedback to bthate@gmail.com, this needs a jabber server to be able to send the feedback.
        the feedback command can be used in a pipeline.
    
    """ 
    if not event.rest and event.inqueue: payload = waitforqueue(event.inqueue, 2000)
    else: payload = event.rest 
    fleet = getfleet()
    feedbackbot = fleet.getfirstjabber()
    if not feedbackbot: event.reply("can't find an xmpp bot to send the feedback with") ; return
    event.reply("sending to bthate@gmail.com")
    feedbackbot.say("bthate@gmail.com", "%s send you this: %s" % (event.userhost, payload), event=event)
    event.done()

cmnds.add("feedback", handle_feedback, ["OPER", "USER", "GUEST"], threaded=True)
examples.add("feedback", "send a message to replies@jsonbot.org", "1) admin-exceptions ! feedback 2) feedback the bot is missing some spirit !")
