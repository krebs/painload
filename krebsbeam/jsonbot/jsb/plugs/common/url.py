# jsb/plugs/common/url.py
#
#

""" maintain log of urls. """

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.lib.callbacks import callbacks
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.persiststate import PlugState

## basic imports

import re
import os

## defines
    
re_url_match  = re.compile(u'((?:http|https)://\S+)')
state = None
initdone = False

## init function

def init():
    global state
    global initdone
    state = PlugState()
    state.define('urls', {})
    initdone = True
    return 1

## size function

def size():
    """ show number of urls. """
    s = 0
    if not initdone: return s
    for i in state['urls'].values():
        for j in i.values(): s += len(j)
    return s

## search function

def search(what, queue):
    """ search the url database. """
    global initdone
    result = []
    if not initdone: return result
    try:
        for i in state['urls'].values():
            for urls in i.values():
                for url in urls:
                    if what in url: result.append(url)
    except KeyError: pass
    for url in result: queue.put_nowait(url)

## url callbacks

def urlpre(bot, ievent):
    return re_url_match.findall(ievent.txt)

def urlcb(bot, ievent):
    if not state: return 
    try:
        test_urls = re_url_match.findall(ievent.txt)
        for i in test_urls:
            if not state['urls'].has_key(bot.cfg.name):
                state['urls'][bot.cfg.name] = {}
            if not state['urls'][bot.cfg.name].has_key(ievent.channel):
                state['urls'][bot.cfg.name][ievent.channel] = []
            if not i in state['urls'][bot.cfg.name][ievent.channel]:
                state['urls'][bot.cfg.name][ievent.channel].append(i)  
        state.save()
    except Exception, ex: handle_exception()

callbacks.add('PRIVMSG', urlcb, urlpre, threaded=True)
callbacks.add('MESSAGE', urlcb, urlpre, threaded=True)
callbacks.add('TORNADO', urlcb, urlpre, threaded=True)

## url-search commands

def handle_urlsearch(bot, ievent):
    """ arguments: <searchtxt> - search the per channel url database for a search term. """
    if not state: ievent.reply('rss state not initialized') ; return
    if not ievent.rest: ievent.missing('<searchtxt>') ; return
    result = []
    try:
        for i in state['urls'][bot.cfg.name][ievent.channel]:
            if ievent.rest in i: result.append(i)
    except KeyError: ievent.reply('no urls known for channel %s' % ievent.channel) ; return
    except Exception, ex: ievent.reply(str(ex)) ; return
    if result: ievent.reply('results matching %s: ' % ievent.rest, result)
    else: ievent.reply('no result found') ; return

cmnds.add('url-search', handle_urlsearch, ['OPER', 'USER', 'GUEST'])
examples.add('url-search', 'search matching url entries', 'url-search jsonbot')

## url-searchall command

def handle_urlsearchall(bot, ievent):
    """ arguments: <searchtxt> - search all urls. """
    if not state: ievent.reply('rss state not initialized') ; return
    if not ievent.rest: ievent.missing('<searchtxt>') ; return
    result = []
    try:
        for i in state['urls'].values():
            for urls in i.values():
                for url in urls:
                    if ievent.rest in url: result.append(url)
    except Exception, ex: ievent.reply(str(ex)) ; return
    if result: ievent.reply('results matching %s: ' % ievent.rest, result)
    else: ievent.reply('no result found') ; return

cmnds.add('url-searchall', handle_urlsearchall, ['OPER', 'USER', 'GUEST'])
examples.add('url-searchall', 'search matching url entries', 'url-searchall jsonbot')

## url-size command

def handle_urlsize(bot, ievent):
    """ no arguments - show number of urls stored. """
    ievent.reply(str(size()))

cmnds.add('url-size', handle_urlsize, 'OPER')
examples.add('url-size', 'show number of urls in cache', 'url-size')
