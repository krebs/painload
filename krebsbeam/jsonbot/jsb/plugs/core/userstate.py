# jsb/plugs/core/userstate.py
#
#

""" userstate is stored in jsondata/state/users/<username>. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.persiststate import UserState
from jsb.lib.errors import NoSuchUser

## set command

def handle_set(bot, ievent):
    """ arguments: <item> <value> - set a variable in your userstate. """
    try: (item, value) = ievent.args
    except ValueError: ievent.missing("<item> <value>") ; return
    ievent.user.state.data[item.lower()] = value
    ievent.user.state.save()
    ievent.reply("%s set to %s" % (item.lower(), value))
    
cmnds.add('set', handle_set, ['OPER', 'USER', 'GUEST'])
examples.add('set', 'set userstate', 'set place heerhugowaard')

## get command

def handle_get(bot, ievent):
    """ arguments: [<searchtxt>] - get your userstate (complete dump or use <searchtxt> to filter). """
    target = ievent.rest
    if target: target = target.lower()
    userstate = ievent.user.state
    result = []
    for i, j in userstate.data.iteritems():
        if target == i or not target: result.append("%s=%s" % (i, j))
    if result: ievent.reply("state: ", result)
    else: ievent.reply('no userstate of %s known' % ievent.userhost)

cmnds.add('get', handle_get, ['OPER', 'USER', 'GUEST'])
examples.add('get', 'get your userstate', 'get')

## unset command

def handle_unset(bot, ievent):
    """ arguments: <item> - remove value from user state of your userstate. """
    try:
        item = ievent.args[0].lower()
    except (IndexError, TypeError):
        ievent.missing('<item>')
        return
    try: del ievent.user.state.data[item]
    except KeyError:
        ievent.reply('no such item')
        return
    ievent.user.state.save()
    ievent.reply('item %s deleted' % item)

cmnds.add('unset', handle_unset, ['USER', 'GUEST'])
examples.add('unset', 'delete variable from your state', 'unset TZ')
