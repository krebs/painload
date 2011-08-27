# jsb/plugs/core/to.py
#
#

""" send output to another user .. used in a pipeline. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.utils.generic import getwho, waitforqueue
from jsb.lib.examples import examples

## to command

def handle_to(bot, ievent):
    """ arguments: <nick> - direct output to <nick>, use this command in a pipeline. """
    if not ievent.inqueue: ievent.reply('use to in a pipeline') ; return
    try: nick = ievent.args[0]
    except IndexError: ievent.reply('to <nick>') ; return
    if nick == 'me': nick = ievent.nick
    if not getwho(bot, nick): ievent.reply("don't know %s" % nick) ; return
    result = waitforqueue(ievent.inqueue, 5000)
    if result:
        bot.say(nick, "%s sends you this:" % ievent.nick)
        bot.say(nick, " ".join(result))
        if len(result) == 1: ievent.reply('1 element sent')
        else: ievent.reply('%s elements sent' % len(result))
    else: ievent.reply('nothing to send')

cmnds.add('to', handle_to, ['OPER', 'USER', 'TO'])
examples.add('to', 'send pipeline output to another user', 'list ! to dunker')
