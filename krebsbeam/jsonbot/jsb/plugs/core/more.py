# jsb/plugs/core/more.py
#
#

""" access the output cache. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.less import outcache

## basic imports

import logging

## more command

def handle_more(bot, ievent):
    """ no arguments - pop message from the output cache. """
    if ievent.msg and bot.type == "irc": target = ievent.nick
    else: target = ievent.channel
    try: txt, size = outcache.more(u"%s-%s" % (bot.cfg.name, target))
    except IndexError: txt = None 
    if not txt: ievent.reply('no more data available for %s' % target) ; return
    txt = bot.outputmorphs.do(txt, ievent)
    if size: txt += "<b> - %s more</b>" % str(size)
    bot.outnocb(target, txt, response=ievent.response, event=ievent)
    bot.outmonitor(ievent.origin or ievent.userhost, ievent.channel, txt)

cmnds.add('more', handle_more, ['USER', 'GUEST'])
examples.add('more', 'return txt from output cache', 'more')
