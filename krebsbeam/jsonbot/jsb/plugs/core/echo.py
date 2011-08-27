# jsb/plugs/common/echo.py
#
#

""" echo typed sentences. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.callbacks import callbacks, first_callbacks, last_callbacks

## basic imports

import logging

## echo-callback

def echopre(bot, event):
    """ test whether we should echo. """
    if event.how != "background" and bot.type in ["tornado", "web"] and not event.forwarded and not event.cbtype == "OUTPUT": return True
    return False

def echocb(bot, event):
    """ do the echo. """
    bot.outnocb(event.channel, event.txt, event=event)

#first_callbacks.add("TORNADO", echocb, echopre)
#first_callbacks.add("DISPATCH", echocb, echopre)

## echo command

def handle_echo(bot, event):
    """ argumetnts: <txt> - echo txt to channel. """
    if event.how != "background" and not event.isremote():
        if not event.isdcc: bot.saynocb(event.channel, u"%s" % event.rest)
            
cmnds.add("echo", handle_echo, ['OPER', 'USER'])
examples.add("echo", "echo input", "echo yoooo dudes")
