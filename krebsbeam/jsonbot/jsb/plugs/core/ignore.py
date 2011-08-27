# jsb/plugs/core/ignore.py
#
#

## jsb imports

from jsb.lib.users import getusers
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.utils.generic import getwho

## ignore command

def handle_ignore(bot, event):
    """ arguments: <nick>|<userhost>|<JID> - ignore a user. """
    if not event.rest: event.missing("<nick>|<userhost>|<JID>") ; return
    nick = event.rest
    userhost = getwho(bot, nick)
    if not userhost: userhost = event.rest
    perms = getusers().getperms(userhost)
    if perms and "OPER" in perms: event.reply("can't ignore OPER") ; return
    if not userhost in bot.ignore: bot.ignore.append(userhost)
    event.reply("%s added to ignore list" % userhost)

cmnds.add("ignore", handle_ignore, ["OPER", "IGNORE"])
examples.add("ignore", "ignore a user or userhost (JID)", "ignore dunker")

## unignore command

def handle_unignore(bot, event):
    """ arguments: <nick>|<userhost>|<JID> - unignore a user. """
    if not event.rest: event.missing("<nick>|<userhost>|<JID>") ; return
    nick = event.rest
    userhost = getwho(bot, nick)
    if not userhost: userhost = event.rest
    if userhost in bot.ignore: bot.ignore.remove(userhost) ; event.reply("%s removed from ignore list" % userhost)
    else: event.reply("%s is not in ignore list" % event.rest)

cmnds.add("unignore", handle_unignore, ["OPER", "IGNORE"])
examples.add("unignore", "unignore a user or userhost (JID)", "unignore dunker")
