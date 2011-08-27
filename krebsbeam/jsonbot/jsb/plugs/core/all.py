# jsb/plugs/core/all.py
#
#

""" output the outputcache to the user. """

# jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.less import outcache
from jsb.lib.examples import examples

def handle_all(bot, event):
    try: nr = int(event.rest)
    except ValueError: nr = None
    if bot.type == "irc": printto = event.nick
    else: printto = event.userhost
    if event.msg and bot.type == "irc": target = event.nick
    else: target = event.channel
    target = "%s-%s" % (bot.cfg.name, target)
    res = outcache.copy(target)
    if res:
        nr = nr or len(res)
        event.reply("sending %s lines from %s to %s" % (nr, target, printto))
        if bot.type in ["xmpp", "sxmpp"]:
            bot.saynocb(printto, "lines from %s" % target, res, event=event, showall=True)
        else:
            for i in res:
                bot.outnocb(printto, i, event=event, showall=True)
    else: event.reply("no data in outputcache of %s (%s)" % (event.channel, bot.cfg.name))

cmnds.add("all", handle_all, ["OPER", "USER", "GUEST"], threaded=True)
examples.add("all", "show all of the output cache (in /msg)", "1) all 2) all 7")
