# jsb/utils/format.py
#
#

""" provide formatting functions. """

## jsb imports

from jsb.utils.name import stripname
from jsb.utils.url import striphtml
from jsb.utils.lazydict import LazyDict

## basic imports

import time
import os
import logging
from datetime import datetime

## formats
# Formats are defined here. simple also provides default values if values
# are not supplied by the format, as well as format 'simple'. 
# Parameters that should be supplied:
#   * timestamp_format: format of timestamp in log files
#     * all strftime vars supported.
#   * filename: file name for log
#     * var channel : full channel ie. #dunkbot
#     * var channel_name : channel without '#' ie. dunkbot
#   * event_filename: 
#        if event_filename exists, then it will be used for
#        logging events (seperate from chat)
#     * var channel : full channel ie. #dunkbot
#     * var channel_name : channel without '#' ie. dunkbot
#   * separator: the separator between the timestamp and message

formats = {
    'log': {
        'timestamp_format': '%Y-%m-%d %H:%M:%S',
        'basepath': None,
        'filename': 'chatlogs/%%(network)s/simple/%%(target)s.%Y%m%d.slog',
        'event_prefix': '',
        'event_filename': 'chatlogs/%%(network)s/simple/%%(channel_name)s.%Y%m%d.slog',
        'separator': ' ',
    },
    'simple': {
        'timestamp_format': '%Y-%m-%d %H:%M:%S',
        'basepath': None,
        'filename': 'chatlogs/%%(network)s/simple/%%(target)s.%Y%m%d.slog',
        'event_prefix': '',
        'event_filename': 'chatlogs/%%(network)s/simple/%%(channel_name)s.%Y%m%d.slog',
        'separator': ' | ',
    },
    'supy': {
        'timestamp_format': '%Y-%m-%dT%H:%M:%S',
        'filename': 'chatlogs/%%(network)s/supy/%%(target)s/%%(target)s.%Y-%m-%d.log',
        'event_prefix': '*** ',
        'event_filename': None,
        'separator': '  ',
    }
}

format = "%(message)s"

## functions

def format_opt(name, format="log"):
    try: simple_format = formats[format]
    except KeyError: return
    f = formats.get(format, 'log')
    opt = f.get(name, simple_format.get(name, None))
    return opt

## formatevent function

def formatevent(bot, ievent, channels, forwarded=False):
    m = {
        'datetime': datetime.now(),
        'separator': format_opt('separator'),
        'event_prefix': format_opt('event_prefix'),
        'network': bot.cfg.networkname,
        'nick': ievent.nick,
        'target': stripname(ievent.channel),
        'botname': bot.cfg.name,
        'txt': ievent.txt,
        'type': ievent.cbtype
    }
    m = LazyDict(m)
    if ievent.cmnd == 'PRIVMSG':
        if ievent.txt.startswith('\001ACTION'): m.txt = '* %s %s' % (m.nick, ievent.txt[7:-1].strip())
        else:
             if bot.type == "irc": m.txt = '<%s> %s' % (m.nick, striphtml(ievent.txt))
             elif not forwarded: m.txt = '<%s> %s' % (m.nick, bot.normalize(ievent.txt))
             else: m.txt = bot.normalize(ievent.txt)
    elif ievent.cmnd == 'NOTICE':
            m.target = ievent.arguments[0]
            m.txt = "-%s- %s"%(ievent.nick, ievent.txt)
    elif ievent.cmnd == 'TOPIC': m.txt = '%s changes topic to "%s"'%(ievent.nick, ievent.txt)
    elif ievent.cmnd == 'MODE':
        margs = ' '.join(ievent.arguments[1:])
        m.txt = '%s sets mode: %s'% (ievent.nick, margs)
    elif ievent.cmnd == 'JOIN': m.txt = '%s (%s) has joined %s'%(ievent.nick, ievent.userhost, ievent.channel)
    elif ievent.cmnd == 'KICK': m.txt = '%s was kicked by %s (%s)'% (ievent.arguments[1], ievent.nick, ievent.txt)
    elif ievent.cmnd == 'PART': m.txt = '%s (%s) has left %s'% (ievent.nick, ievent.userhost, ievent.channel)
    elif ievent.cmnd in ('QUIT', 'NICK'):
        if not ievent.user or not ievent.user.data.channels:
            logging.debug("chatlog - can't find joined channels for %s" % ievent.userhost)
            return m
        cmd = ievent.cmnd
        nick = cmd == 'NICK' and ievent.txt or ievent.nick
        for c in event.user.channels:
            if [bot.cfg.name, c] in channels:
                if True:
                    if cmd == 'NICK': m.txt = '%s (%s) is now known as %s'% (ievent.nick, ievent.userhost, ievent.txt)
                    else: m.txt= '%s (%s) has quit: %s'% (ievent.nick, ievent.userhost, ievent.txt)
                    m.type = ievent.cmnd.lower()
                    m.target = c
    elif ievent.cbtype == 'PRESENCE':
            if ievent.type == 'unavailable': m.txt = "%s left" % ievent.nick
            else: m.txt = "%s joined" % ievent.nick
    return m
