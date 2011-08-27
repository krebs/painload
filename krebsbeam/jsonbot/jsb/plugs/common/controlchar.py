# jsb/plugs/common/controlchar.py
#
#

"""
    command to control the control (command) characters. The cc is a string 
    containing the allowed control characters.

"""

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples

## cc command

def handle_cc(bot, ievent):
    """ arguments: [<controlchar>] - set/get control character of channel. """
    try:
        what = ievent.args[0]
        if not bot.users.allowed(ievent.userhost, 'OPER'): return
        if len(what) > 1:
            ievent.reply("only one character is allowed")
            return
        try: ievent.chan.data.cc = what
        except (KeyError, TypeError):
            ievent.reply("no channel %s in database" % chan)
            return
        ievent.chan.save()
        ievent.reply('control char set to %s' % what)
    except IndexError:
        try:
            cchar = ievent.chan.data.cc
            ievent.reply('controlchar are/is %s' % cchar)
        except (KeyError, TypeError): ievent.reply("default cc is %s" % bot.cfg['defaultcc'])

cmnds.add('cc', handle_cc, 'USER')
examples.add('cc', 'set control char of channel or show control char of channel','1) cc ! 2) cc')

## cc-add command

def handle_ccadd(bot, ievent):
    """ arguments: <character> - add a control char to the channels cc list. """
    try:
        what = ievent.args[0]
        if not bot.users.allowed(ievent.userhost, 'OPER'): return
        if len(what) > 1:
            ievent.reply("only one character is allowed")
            return
        try: ievent.chan.data.cc += what
        except (KeyError, TypeError):
            ievent.reply("no channel %s in database" % ievent.channel)
            return
        ievent.chan.save()
        ievent.reply('control char %s added' % what)
    except IndexError: ievent.missing('<cc> [<channel>]')

cmnds.add('cc-add', handle_ccadd, 'OPER', allowqueue=False)
examples.add('cc-add', 'cc-add <control char> .. add control character', 'cc-add #')

## cc-del command

def handle_ccdel(bot, ievent):
    """ arguments: <character> - remove a control char from the channels cc list. """
    try:
        what = ievent.args[0]
        if not bot.users.allowed(ievent.userhost, 'OPER'): return
        if len(what) > 1:
            ievent.reply("only one character is allowed")
            return
        if ievent.chan.data.cc:
            ievent.chan.data.cc = ievent.chan.data.cc.replace(what, '')
            ievent.chan.save()
        ievent.reply('control char %s deleted' % what)
    except IndexError: ievent.missing('<cc> [<channel>]')

cmnds.add('cc-del', handle_ccdel, 'OPER')
examples.add('cc-del', 'cc-del <control character> .. remove cc', 'cc-del #')
