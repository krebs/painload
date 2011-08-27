# jsb/plugs/core/xmpp.py
#
#

""" xmpp related commands. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.fleet import getfleet

## xmpp-invite command

def handle_xmppinvite(bot, event):
    """ arguments: <list of JIDs> - invite (subscribe to) a different user. """
    if not event.rest:
        event.missing("<list of JIDs>")
        return
    bot = getfleet().getfirstjabber()
    if bot:
        for jid in event.args: bot.invite(jid)
        event.done()
    else: event.reply("can't find jabber bot in fleet")

cmnds.add("xmpp-invite", handle_xmppinvite, 'OPER')
examples.add("xmpp-invite", "invite a user.", "xmpp-invite jsoncloud@appspot.com")
