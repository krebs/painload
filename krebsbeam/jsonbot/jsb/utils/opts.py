# jsb/utils/opts.py
#
#

""" options related functions. """

## jsb imports

from jsb.lib.errors import NameNotSet
from jsb.lib.config import Config
from jsb.version import version
from jsb.utils.name import stripname

## basic imports

import os
import uuid
import logging
import optparse

## EventOptionParser class

class EventOptionParser(optparse.OptionParser):

     def exit(self):
         pass

     def error(self):
         pass

## makeopts function

def makeircopts(txt=""):
    """ create commandline parser options. """
    parser = optparse.OptionParser(usage='usage: %prog [options]', version=version)
    parser.add_option('', '-r', type='string', default=False, dest='doresume',  metavar='PATH', 
                  help="resume the bot from the folder specified")
    parser.add_option('-d', '--datadir', type='string', default=False, dest='datadir',  help="datadir of the bot")
    parser.add_option('-o', '--owner', type='string', default=False, dest='owner',  help="owner of the bot")
    parser.add_option('-s', '--server', type='string', default=False, dest='server',  help="server to connect to (irc)")
    parser.add_option('-c', '--channel', type='string', default=False, dest='channel',  help="channel to join")
    parser.add_option('-l', '--loglevel', type='string', default="", dest='loglevel',  help="loglevel of the bot")
    parser.add_option('-p', '--password', type='string', default=False, dest='password', help="set password used to connect to the server")
    parser.add_option('', '--name', type='string', default=False, dest='name', help="bot's name")
    parser.add_option('', '--port', type='string', default=False, dest='port',  help="set port of server to connect to")
    parser.add_option('', '--save', action='store_true', default=False, dest='save',  help="save to config file")
    parser.add_option('', '--colors', action='store_true', default=False, dest='colors',  help="enable the use of colors")
    parser.add_option('-n', '--nick', type='string', default=False, dest='nick',  help="nick of the bot")
    parser.add_option('', '--ssl', action='store_true', default=False, dest='ssl',  help="use ssl")
    parser.add_option('-y', '--nossl', action='store_true', default=False, dest='nossl',  help="don't use ssl")
    parser.add_option('-6', '--ipv6', action='store_true', default=False, dest='ipv6', help="enable ipv6 bot")
    parser.add_option('-u', '--username', type="string", default=False, dest='username', help="user to auth to server with")
    if txt: opts, args = parser.parse_args(txt.split())
    else: opts, args = parser.parse_args()
    opts.args = args
    return opts

## makeconvoreopts

def makeconvoreopts(txt=""):
    """ create commandline parser options. """
    parser = optparse.OptionParser(usage='usage: %prog [options]', version=version)
    parser.add_option('-d', '--datadir', type='string', default=False, dest='datadir',  help="datadir of the bot")
    parser.add_option('-o', '--owner', type='string', default=False, dest='owner',  help="owner of the bot")
    parser.add_option('-l', '--loglevel', type='string', default="", dest='loglevel',  help="loglevel of the bot")
    parser.add_option('-p', '--password', type='string', default=False, dest='password', help="set password used to connect to the server")
    parser.add_option('-c', '--channel', type='string', default=False, dest='channel',  help="channel to join")
    parser.add_option('', '--name', type='string', default=False, dest='name', help="bot's name")
    parser.add_option('', '--colors', action='store_true', default=False, dest='colors',  help="enable the use of colors")
    parser.add_option('-u', '--username', type='string', default=False, dest='username',  help="username of the bot")
    if txt: opts, args = parser.parse_args(txt.split())
    else: opts, args = parser.parse_args()
    opts.args = args
    return opts

## makexmppopts

def makesxmppopts(txt=""):
    """ create commandline parser options. """
    parser = optparse.OptionParser(usage='usage: %prog [options]', version=version)
    parser.add_option('', '-r', type='string', default=False, dest='doresume',  metavar='PATH', 
                  help="resume the bot from the folder specified")
    parser.add_option('-d', '--datadir', type='string', default=False, dest='datadir',  help="datadir of the bot")
    parser.add_option('-u', '--user', type='string', default=False, dest='user',  help="JID of the bot")
    parser.add_option('-o', '--owner', type='string', default=False, dest='owner',  help="owner of the bot")
    parser.add_option('-s', '--server', type='string', default=False, dest='server',  help="server to connect to (irc)")
    parser.add_option('-c', '--channel', type='string', default=False, dest='channel',  help="channel to join")
    parser.add_option('-l', '--loglevel', type='string', default="", dest='loglevel',  help="loglevel of the bot")
    parser.add_option('-p', '--password', type='string', default=False, dest='password', help="set password used to connect to the server")
    parser.add_option('', '--name', type='string', default=False, dest='name', help="bot's name")
    parser.add_option('', '--port', type='string', default=False, dest='port',  help="set port of server to connect to")
    parser.add_option('', '--save', action='store_true', default=False, dest='save',  help="save to config file")
    parser.add_option('', '--colors', action='store_true', default=False, dest='colors',  help="enable the use of colors")
    parser.add_option('-n', '--nick', type='string', default=False, dest='nick',  help="nick of the bot")
    if txt: opts, args = parser.parse_args(txt.split())
    else: opts, args = parser.parse_args()
    opts.args = args
    return opts

## makeconsoleopts

def makeconsoleopts():
    """ create option parser for events. """
    parser = optparse.OptionParser(usage='usage: %prog [options]', version=version)
    parser.add_option('-d', '--datadir', type='string', default=False, dest='datadir',  help="datadir of the bot")
    parser.add_option('-l', '--loglevel', type='string', default="", dest='loglevel',  help="loglevel of the bot")
    parser.add_option('', '--name', type='string', default=False, dest='name', help="bot's name")
    parser.add_option('-x', '--exec', type='string', default="", dest='command', help="give a command to execute")
    parser.add_option('', '--colors', action='store_true', default=False, dest='colors',  help="enable the use of colors")
    try: opts, args = parser.parse_args()
    except Exception, ex: logging.warn("opts - can't parse %s" % txt) ; return
    opts.args = args
    return opts

## makefleetopts function

def makefleetopts():
    """ create option parser for events. """
    parser = optparse.OptionParser(usage='usage: %prog [options] [list of bot names]', version=version)
    parser.add_option('-a', '--all', action='store_true', default=False, dest='all', help="show available fleet bots")
    parser.add_option('-s', '--show', action='store_true', default=False, dest='show', help="print available fleet bots")
    parser.add_option('-d', '--datadir', type='string', default=False, dest='datadir',  help="datadir of the bot")
    parser.add_option('-l', '--loglevel', type='string', default="", dest='loglevel',  help="loglevel of the bot")
    parser.add_option('-o', '--owner', type='string', default=False, dest='owner',  help="owner of the bot")
    parser.add_option('', '--colors', action='store_true', default=False, dest='colors',  help="enable the use of colors")
    parser.add_option('', '-r', type='string', default=False, dest='doresume',  metavar='PATH', 
                  help="resume the bot from the folder specified")
    try: opts, args = parser.parse_args()
    except Exception, ex: logging.warn("opts - can't parse %s" % txt) ; return
    opts.args = args
    return opts

## makeeventopts function

def makeeventopts(txt):
    """ create option parser for events. """
    parser = EventOptionParser()
    parser.add_option('', '--chan', type='string', default=False, dest='channel', help="target channel")
    parser.add_option('-c', '--chan-default', action='store_true', default=False, dest='dochan',  help="use the channel command is given in")
    parser.add_option('-s', '--silent', action='store_true', default=False, dest='silent',  help="give bot response in /pm")
    try: opts, args = parser.parse_args(txt.split())
    except Exception, ex: logging.warn("opts - can't parse %s" % txt) ; return
    opts.args = args
    return opts

## makeconfig function

def makeconsoleconfig(opts=None, botname=None):
    """ make config file based on options. """
    if not botname: botname = opts.name or "default-console" 
    botname = stripname(botname)
    cfg = Config('fleet' + os.sep + botname + os.sep + 'config')
    cfg.type = "console"
    cfg.name = botname
    if opts and opts.loglevel: cfg.loglevel = opts.loglevel
    else: cfg.loglevel = cfg.loglevel or "error"
    return cfg

## makeircconfig function

def makeircconfig(opts=None, botname=None):
    """ make config file based on options. """
    if not opts: botname = botname or "default-irc"
    else:
        if not botname: botname = opts.name or "default-irc"
    botname = stripname(botname)
    cfg = Config('fleet' + os.sep + botname + os.sep + 'config')
    cfg.type = 'irc'
    cfg.name = botname
    if not opts:
        cfg.password = cfg.password or ""
        cfg.ssl = cfg.ssl or False
        cfg.port = cfg.port or 6667
        cfg.server = cfg.server or "localhost"
        cfg.owner = cfg.owner or []
        cfg.ipv6 = cfg.ipv6 or False
        cfg.nick = cfg.nick or "jsb"
        cfg.channels = []
        return cfg          
    if not cfg.channels: cfg.channels = []
    if not cfg.disable: cfg.disable = False
    if opts.password: cfg.password = opts.password
    if opts.ipv6: cfg.ipv6 = True
    else: cfg.ipv6 = cfg.ipv6 or False
    if opts.ssl: cfg.ssl = True
    else: cfg.ssl = cfg.ssl or False
    if opts.nossl: cfg.ssl = False
    if opts.port: cfg.port = opts.port or cfg.port or 6667
    else: cfg.port = cfg.port or 6667
    if opts.server: cfg.server = opts.server
    else: cfg.server = cfg.server or "localhost"
    if not cfg.owner: cfg.owner = []
    if opts.owner and opts.owner not in cfg.owner: cfg.owner.append(opts.owner)
    if opts.ipv6: cfg.ipv6 = opts.ipv6
    if opts.nick: cfg.nick = opts.nick
    else: cfg.nick = cfg.nick or "jsb"
    if opts.username: cfg.username = opts.username
    else: cfg.username = cfg.username or "jsonbot"
    if opts.channel:
        if not opts.channel in cfg.channels: cfg.channels.append(opts.channel)
    else: cfg.channels = cfg.channels or []
    return cfg

## makexmppconfig function

def makesxmppconfig(opts=None, botname=None):
    """ make config file based on options. """
    if not opts: botname = botname or "default-sxmpp"
    else:
        if not botname: botname = opts.name or "default-sxmpp"
    botname = stripname(botname)
    cfg = Config('fleet' + os.sep + botname + os.sep + 'config')
    cfg.type = "sxmpp"
    cfg.name = botname
    if not opts:
        cfg.user = cfg.user or ""
        cfg.host = cfg.host or ""
        cfg.password =  cfg.passord or ""
        cfg.server = cfg.server or ""
        cfg.owner = cfg.owner or []
        cfg.loglevel = cfg.lowlevel or "warn" 
        cfg.nick = cfg.nick or "jsb"
        cfg.channels = []
        return cfg        
    if not cfg.disable: cfg.disable = False
    if not cfg.channels: cfg.channels = []
    if opts.user: cfg.user = opts.user
    else: cfg.user = cfg.user or "%s@jsonbot.org" % cfg.uuid
    if opts.user:
        try: cfg.host = opts.user.split('@')[1]
        except (IndexError, ValueError): print "user is not in the nick@server format"
    if not cfg.host:
        try: cfg.host = cfg.user.split('@')[1]
        except (IndexError, ValueError): print "user is not in the nick@server format"
    if opts.password: cfg.password = opts.password
    if opts.server: cfg.server = opts.server
    else: cfg.server = cfg.server or ""
    if opts.name: cfg.jid = opts.name
    if not cfg.owner: cfg.owner = []
    if opts.owner and opts.owner not in cfg.owner: cfg.owner.append(opts.owner)
    if opts.nick: cfg.nick = opts.nick
    else: cfg.nick = cfg.nick or "jsb"
    if opts.channel:
        if not opts.channel in cfg.channels: cfg.channels.append(opts.channel)
    else: cfg.channels = cfg.channels or []
    return cfg
