# jsb/plugs/common/tinyurl.py
#
#

""" tinyurl.com feeder """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'

## jsb imports

from jsb.lib.commands import cmnds
from jsb.utils.url import striphtml, useragent
from jsb.lib.examples import examples
from jsb.utils.exception import handle_exception
from jsb.lib.persistconfig import PersistConfig

## google imports

try:
    import waveapi
    from google.appengine.api.memcache import get, set
except ImportError: 
    from jsb.lib.cache import get, set

## plug config

plugcfg = PersistConfig()
plugcfg.define("url", 'http://tinyurl.com/create.php')

## simpljejson

from jsb.imports import getjson
json = getjson()

## basic imports

import urllib
import urllib2
import urlparse
import re
import logging

## defines

re_url_match  = re.compile(u'((?:http|https)://\S+)')
urlcache = {}

## functions

def valid_url(url):
    """ check if url is valid """
    if not re_url_match.search(url): return False
    parts = urlparse.urlparse(url)
    cleanurl = '%s://%s' % (parts[0], parts[1])
    if parts[2]: cleanurl = '%s%s' % (cleanurl, parts[2])
    if parts[3]: cleanurl = '%s;%s' % (cleanurl, parts[3])
    if parts[4]: cleanurl = '%s?%s' % (cleanurl, parts[4])
    return cleanurl

## callbacks

def precb(bot, ievent):
    test_url = re_url_match.search(ievent.txt)
    if test_url: return True

def privmsgcb(bot, ievent):
    """ callback for urlcaching """
    test_url = re_url_match.search(ievent.txt)
    if test_url:
        url = test_url.group(1)
        if not urlcache.has_key(bot.cfg.name): urlcache[bot.cfg.name] = {}
        urlcache[bot.cfg.name][ievent.target] = url

# not enabled right now
#callbacks.add('PRIVMSG', privmsgcb, precb)

def get_tinyurl(url):
    """ grab a tinyurl. """
    res = get(url, namespace='tinyurl') ; logging.debug('tinyurl - cache - %s' % unicode(res))
    if res and res[0] == '[': return json.loads(res)
    postarray = [
        ('submit', 'submit'),
        ('url', url),
        ]
    postdata = urllib.urlencode(postarray)
    req = urllib2.Request(url=plugcfg.url, data=postdata)
    req.add_header('User-agent', useragent())
    try: res = urllib2.urlopen(req).readlines()
    except urllib2.URLError, e: logging.warn('tinyurl - %s - URLError: %s' % (url, str(e))) ; return
    except urllib2.HTTPError, e: logging.warn('tinyurl - %s - HTTP error: %s' % (url, str(e))) ; return
    except Exception, ex:
        if "DownloadError" in str(ex): logging.warn('tinyurl - %s - DownloadError: %s' % (url, str(e)))
        else: handle_exception()
        return
    urls = []
    for line in res:
        if line.startswith('<blockquote><b>'): urls.append(striphtml(line.strip()).split('[Open')[0])
    if len(urls) == 3: urls.pop(0)
    set(url, json.dumps(urls), namespace='tinyurl')
    return urls

## tinyurl command

def handle_tinyurl(bot, ievent):
    """ arguments: <url> - get tinyurl from provided url. """
    if not ievent.rest and (not urlcache.has_key(bot.cfg.name) or not urlcache[bot.cfg.name].has_key(ievent.target)):
        ievent.missing('<url>')
        return
    elif not ievent.rest: url = urlcache[bot.cfg.name][ievent.target]
    else: url = ievent.rest
    url = valid_url(url)
    if not url: ievent.reply('invalid or bad URL') ; return
    tinyurl = get_tinyurl(url)
    if tinyurl: ievent.reply(' .. '.join(tinyurl))
    else: ievent.reply('failed to create tinyurl')

cmnds.add('tinyurl', handle_tinyurl, ['OPER', 'USER', 'GUEST'], threaded=True)
examples.add('tinyurl', 'show a tinyurl', 'tinyurl http://jsonbbot.org')
