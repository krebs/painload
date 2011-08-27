# jsb/plugs/core/irc.py
#
#

""" irc related commands. """

## jsb imports

from jsb.lib.callbacks import callbacks
from jsb.lib.partyline import partyline
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.fleet import getfleet
from jsb.lib.wait import waiter
import jsb.lib.threads as thr

## basic imports

import Queue
import sets
import time

## define

ignorenicks = []

## broadcast command

def handle_broadcast(bot, ievent):
    """ arguments: <txt> - broadcast txt to all joined channels. """
    if not ievent.rest:
         ievent.missing('<txt>')
         return
    ievent.reply('broadcasting')
    getfleet().broadcast(ievent.rest)
    partyline.say_broadcast(ievent.rest)
    ievent.reply('done')

cmnds.add('broadcast', handle_broadcast, 'OPER')
examples.add('broadcast', 'send a message to all channels and dcc users', 'broadcast good morning')

## jump command

def handle_jump(bot, ievent):
    """ arguments: <server> <port> - change server. """
    if bot.jabber:
        ievent.reply('jump only works on irc bots')
        return
    if len(ievent.args) != 2:
        ievent.missing('<server> <port>')
        return
    (server, port) = ievent.args
    ievent.reply('changing to server %s' % server)
    bot.shutdown()
    bot.cfg.server = server
    bot.cfg.port = port
    bot.connect()
    ievent.done()

cmnds.add('jump', handle_jump, 'OPER')
examples.add('jump', 'jump <server> <port> .. switch server', 'jump localhost 6667')

## nick command

def handle_nick(bot, ievent):
    """ arguments: <nickname> - change bot's nick. """
    if bot.jabber:
        ievent.reply('nick works only on irc bots')
        return
    try: nick = ievent.args[0]
    except IndexError:
        ievent.missing('<nickname>')
        return
    ievent.reply('changing nick to %s' % nick)
    bot.donick(nick, setorig=True, save=True)
    ievent.done()

cmnds.add('nick', handle_nick, 'OPER', threaded=True)
examples.add('nick', 'nick <nickname> .. set nick of the bot', 'nick mekker')

## sendraw command

def handle_sendraw(bot, ievent):
    """ arguments: <txt> - send raw text to the server. """
    ievent.reply('sending raw txt')
    bot._raw(ievent.rest)
    ievent.done()

cmnds.add('sendraw', handle_sendraw, ['OPER', 'SENDRAW'])
examples.add('sendraw', 'sendraw <txt> .. send raw string to the server', 'sendraw PRIVMSG #test :yo!')

## nicks command

nickresult = []

def handle_nicks(bot, event):
    """ no arguments - return nicks on channel. """
    if bot.type != 'irc': event.reply('nicks only works on irc bots') ; return

    def aggregate(bot, e):
        global nickresult
        nickresult.extend(e.txt.split())

    def nickscb(bot, e):
        global nickresult
        event.reply("nicks on %s (%s): " % (event.channel, bot.cfg.server), nickresult)
        nickresult = []
        waiter.remove("jsb.plugs.core.irc")

    w353 = waiter.register('353', aggregate)
    w366 = waiter.register('366', nickscb)
    event.reply('searching for nicks')
    bot.names(event.channel)
    time.sleep(5)
    waiter.ready(w353)
    waiter.ready(w366)

cmnds.add('nicks', handle_nicks, ['OPER', 'USER'], threaded=True)
examples.add('nicks', 'show nicks on channel the command was given in', 'nicks')

## reconnect command

def handle_reconnect(bot, ievent):
    """ no arguments - reconnect .. reconnect to server. """
    ievent.reply('reconnecting')
    bot.reconnect()
    ievent.done()

cmnds.add('reconnect', handle_reconnect, 'OPER', threaded=True)
examples.add('reconnect', 'reconnect to server', 'reconnect')

## action command

def handle_action(bot, ievent):
    """ arguments: <channel> <txt> - make the bot send an action string. """
    try: channel, txt = ievent.rest.split(' ', 1)
    except ValueError:
        ievent.missing('<channel> <txt>')
        return
    bot.action(channel, txt)

cmnds.add('action', handle_action, ['ACTION', 'OPER'])
examples.add('action', 'send an action message', 'action #test yoo dudes')

## say command

def handle_say(bot, ievent):
    """ aguments: <channel> <txt> - make the bot say something. """
    try: channel, txt = ievent.rest.split(' ', 1)
    except ValueError:
        ievent.missing('<channel> <txt>')
        return
    bot.say(channel, txt)

cmnds.add('say', handle_say, ['SAY', 'OPER'], speed=1)
examples.add('say', 'send txt to channel/user', 'say #test good morning')

## server command

def handle_server(bot, ievent):
    """ no arguments - show the server to which the bot is connected. """
    ievent.reply(bot.cfg.server or "not connected.")

cmnds.add('server', handle_server, 'OPER')
examples.add('server', 'show server hostname of bot', 'server')

## voice command

def handle_voice(bot, ievent):
    """ arguments: <nick> - give voice. """
    if bot.type != 'irc':
        ievent.reply('voice only works on irc bots')
        return
    if len(ievent.args)==0:
        ievent.missing('<nickname>')
        return
    ievent.reply('setting voice on %s' % str(ievent.args))
    for nick in sets.Set(ievent.args): bot.voice(ievent.channel, nick)
    ievent.done()

cmnds.add('voice', handle_voice, 'OPER')
examples.add('voice', 'give voice to user', 'voice test')
