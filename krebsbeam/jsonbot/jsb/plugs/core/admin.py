# jsb/plugs/core.admin.py
#
#

""" admin related commands. these commands are mainly for maintaining the bot. """

## jsb imports

from jsb.lib.eventhandler import mainhandler
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.persist import Persist
from jsb.lib.boot import savecmndtable, savepluginlist, boot, plugin_packages, clear_tables, getcmndtable, getcallbacktable
from jsb.lib.plugins import plugs
from jsb.lib.botbase import BotBase
from jsb.lib.exit import globalshutdown
from jsb.lib.config import getmainconfig
from jsb.utils.generic import stringsed
from jsb.utils.exception import handle_exception

## basic imports

import logging

## admin-boot command

def handle_adminboot(bot, ievent):
    """ no arguments - boot the bot .. do some initialisation. """
    if 'saveperms' in ievent.rest: boot(force=True, saveperms=True, clear=True)
    else: boot(force=True, saveperms=False, clear=True)
    ievent.done()

cmnds.add('admin-boot', handle_adminboot, 'OPER')
examples.add('admin-boot', 'initialize the bot .. cmndtable and pluginlist', 'admin-boot')

## admin-commands command

def handle_admincommands(bot, ievent):
    """ no arguments - load all available plugins. """
    cmnds = getcmndtable()
    if not ievent.rest: ievent.reply("commands: ", cmnds)
    else:
        try: ievent.reply("%s command is found in %s " % (ievent.rest, cmnds[ievent.rest]))
        except KeyError: ievent.reply("no such commands available") 

cmnds.add('admin-commands', handle_admincommands, 'OPER')
examples.add('admin-commands', 'show runtime command table', 'admin-commands')

## admin-callbacks command

def handle_admincallbacks(bot, ievent):
    """ no arguments - load all available plugins. """
    cbs = getcallbacktable()
    if not ievent.rest: ievent.reply("callbacks: ", cbs)
    else:
        try: ievent.reply("%s callbacks: " % ievent.rest, cbs[ievent.rest])
        except KeyError: ievent.reply("no such callbacks available") 

cmnds.add('admin-callbacks', handle_admincallbacks, 'OPER')
examples.add('admin-callbacks', 'show runtime callback table', 'admin-callbacks')

## admin-userhostcache command

def handle_userhostscache(bot, ievent):
    """ no arguments - show userhostscache of the bot the command is given on. """
    ievent.reply("userhostcache of %s: " % ievent.channel, bot.userhosts.keys() + bot.userhosts.values())

cmnds.add('admin-userhostscache', handle_userhostscache, 'OPER')
examples.add('admin-userhostscache', 'show userhostscache ', 'admin-userhostscache')

## admin-loadall command

def handle_loadall(bot, ievent):
    """ no arguments - load all available plugins. """
    plugs.loadall(plugin_packages, force=True)
    ievent.done()

cmnds.add('admin-loadall', handle_loadall, 'OPER', threaded=True)
examples.add('admin-loadall', 'load all plugins', 'admin-loadall')

## admin-makebot command

def handle_adminmakebot(bot, ievent):
    """ arguments: <botname> <bottype> - create a bot of given type. """
    try: botname, bottype = ievent.args
    except ValueError: ievent.missing("<name> <type>") ; return
    newbot = BotBase()
    newbot.botname = botname
    newbot.type = bottype
    newbot.owner = bot.owner
    newbot.save()
    ievent.done()

cmnds.add('admin-makebot', handle_adminmakebot, 'OPER')
examples.add('admin-makebot', 'create a bot', 'admin-makebot cmndxmpp xmpp')

## admin-stop command

def handle_adminstop(bot, ievent):
    """ no arguments - stop the bot. """
    if bot.isgae: ievent.reply("this command doesn't work on the GAE") ; return
    mainhandler.put(0, globalshutdown)

cmnds.add("admin-stop", handle_adminstop, "OPER")
examples.add("admin-stop", "stop the bot.", "stop")

## admin-upgrade command

def handle_adminupgrade(bot, event):
    """ no arguments - upgrade from 0.5 to 0.6. """
    if not bot.isgae: event.reply("this command only works in GAE") ; return
    else: import google
    from jsb.lib.persist import JSONindb
    teller = 0
    props = JSONindb.properties()
    for d in JSONindb.all():
        try:
            dd = d.filename
            if not "gozerdata" in dd: continue
            if 'run' in dd: continue
            ddd = stringsed(dd, "s/%s/%s/" % ("gozerdata", "data"))
            ddd = stringsed(ddd, "s/waveplugs/jsb.plugs.wave/")
            ddd = stringsed(ddd, "s/gozerlib\.plugs/jsb.plugs.core/")
            ddd = stringsed(ddd, "s/commonplugs/jsb.plugs.common/")  
            ddd = stringsed(ddd, "s/socketplugs/jsb.plugs.socket/")  
            ddd = stringsed(ddd, "s/gaeplugs/jsb.plugs.gae/")
            if d.get_by_key_name(ddd): continue 
            d.filename = ddd
            kwds = {}
            for prop in props: kwds[prop] = getattr(d, prop)
            d.get_or_insert(ddd, **kwds)
            bot.say(event.channel, "UPGRADED %s" % ddd)
            teller += 1
        except Exception, ex: bot.say(event.channel, str(ex))
    bot.say(event.channel, "DONE - upgraded %s items" % teller)

cmnds.add("admin-upgrade", handle_adminupgrade, "OPER", threaded=True)
examples.add("admin-upgrade", "upgrade the GAE bot", "admin-upgrade")

## admin-setstatus command

def handle_adminsetstatus(bot, event):
    """ arguments: <status> [<statustxt>] - set the status of the bot (xmpp). """
    if bot.type != "sxmpp": event.reply("this command only works on sxmpp bots (for now)") ; return
    if not event.rest: event.missing("<status> [<show>]") ; return
    status = event.args[0]
    try: show = event.args[1]
    except IndexError: show = ""
    bot.setstatus(status, show)

cmnds.add("admin-setstatus", handle_adminsetstatus, ["STATUS", "OPER"])
examples.add("admin-setstatus", "set status of sxmpp bot", "admin-setstatus available Yooo dudes !")

## admin-reloadconfig command

def handle_adminreloadconfig(bot, event):
    """ no arguments - reload bot config and mainconfig files. """
    try:
        bot.cfg.reload()
        getmainconfig().reload()
    except Exception, ex: handle_exception()
    event.done()

cmnds.add("admin-reloadconfig", handle_adminreloadconfig, ["OPER"])
examples.add("admin-reloadconfig", "reload mainconfig", "admin-reloadconfig")

def handle_adminexceptions(bot, event):
    """ no arguments - show exceptions raised in the bot. """
    from jsb.utils.exception import exceptionlist, exceptionevents
    for e, ex in exceptionevents: logging.warn("%s - exceptions raised is %s" % (e.bot.cfg.name, ex))
    event.reply("exceptions raised: ", exceptionlist)

cmnds.add("admin-exceptions", handle_adminexceptions, ["OPER"])
examples.add("admin-exceptions", "show exceptions raised", "admin-exceptions")

def handle_admindebugon(bot, event):
    """ no arguments - enable debug on a channel. """
    event.chan.data.debug = True;
    event.chan.save()
    event.reply("debugging is enabled for %s" % event.channel)

cmnds.add("admin-debugon", handle_admindebugon, ['OPER', ])
examples.add("admin-debugon", "enable debug on a channel.", "admin-debugon")

def handle_admindebugoff(bot, event):
    """ no arguments - disable debug on a channel. """
    event.chan.data.debug = False;
    event.chan.save()
    event.reply("debugging is disabled for %s" % event.channel)

cmnds.add("admin-debugoff", handle_admindebugoff, ['OPER', ])
examples.add("admin-debugoff", "disable debug on a channel.", "admin-debugoff")

def handle_adminmc(bot, event):
    """ flush memcached. """
    if event.rest == "stats":
        try:
            from jsb.memcached import mc
            test = mc.get_stats()
            if not test: event.reply("no memcached found")
            else: event.reply("memcached stats: ", test[0][1])
        except Exception, ex:
            event.reply("memcached error: %s" % str(ex))
    elif event.rest == "flushall":
        try:
            from jsb.memcached import mc
            if mc: test = mc.flush_all() ; event.done()
            else: event.reply("no memcached running")
        except Exception, ex:
            event.reply("memcached error: %s" % str(ex))
    else: event.reply("choose one of stats, flushall")

cmnds.add("admin-mc", handle_adminmc, "OPER")
examples.add("admin-mc", "bots interdace to memcached", "1) admin-mc stats 2) admin-mc flushall")
