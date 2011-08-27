# jsb/plugs/common/rss.py
#
#

"""
    the rss mantra is of the following:

    1) add a url with !rss-add <feedname> <url>
    2) use !rss-start <feed> in the channel you want the feed to appear
    3) run !rss-scan <feed> to see what tokens you can use .. add them with !rss-additem <feed> <token>
    4) change markup with !rss-addmarkup <feed> <markupitem> <value> .. see !rss-markuplist for possible markups
    5) check with !rss-feeds in a channel to see what feeds are running in a channel
    6) in case of trouble check !rss-running to see what feeds are monitored
    7) enjoy
    
"""

## jsb imports

from jsb.lib.persist import Persist, PlugPersist
from jsb.utils.url import geturl2, striphtml, useragent
from jsb.utils.exception import handle_exception
from jsb.utils.generic import strippedtxt, fromenc, toenc, jsonstring, getwho
from jsb.utils.rsslist import rsslist
from jsb.utils.lazydict import LazyDict
from jsb.utils.statdict import StatDict
from jsb.utils.timeutils import strtotime
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.utils.dol import Dol
from jsb.utils.pdod import Pdod
from jsb.utils.pdol import Pdol
from jsb.lib.users import users
from jsb.utils.id import getrssid
from jsb.lib.tasks import taskmanager
from jsb.lib.callbacks import callbacks
from jsb.lib.fleet import getfleet
from jsb.lib.threadloop import TimedLoop
from jsb.lib.threads import start_new_thread
from jsb.lib.errors import NoSuchBotType, FeedAlreadyExists, NameNotSet
from jsb.lib.datadir import getdatadir
from jsb.lib.channelbase import ChannelBase
from jsb.imports import getfeedparser, getjson


## google imports

try: import waveapi ; from google.appengine.api.memcache import get, set, delete
except ImportError: from jsb.lib.cache import get, set, delete

## tinyurl import

try: from jsb.plugs.common.tinyurl import get_tinyurl
except ImportError:
    def get_tinyurl(url):
        return [url, ]

## basic imports

import time
import os
import types
import thread
import socket
import xml
import logging
import datetime
import hashlib
import copy
import re

## exceptions

class RssException(Exception):
    pass

class Rss301(RssException):
    pass

class RssStatus(RssException):
    pass

class RssBozoException(RssException):
    pass

class RssNoSuchItem(RssException):
    pass

## defines

feedparser = getfeedparser()
json = getjson()

cpy = copy.deepcopy

allowedtokens = ['updated', 'link', 'summary', 'tags', 'author', 'content', 'title', 'subtitle']
savelist = []

possiblemarkup = {'separator': 'set this to desired item separator', \
'all-lines': "set this to 1 if you don't want items to be aggregated", \
'tinyurl': "set this to 1 when you want to use tinyurls", 'skipmerge': \
"set this to 1 if you want to skip merge commits", 'reverse-order': \
'set this to 1 if you want the rss items displayed with oldest item first', \
'nofeedname': "if you don't want the feedname shown"}

## global data

lastpoll = PlugPersist('lastpoll')
if not lastpoll.data: lastpoll.data = LazyDict() ; lastpoll.save()

sleeptime = PlugPersist('sleeptime')
if not sleeptime.data: sleeptime.data = LazyDict() ; sleeptime.save()

runners = PlugPersist('runners')
if not runners.data: runners.data = LazyDict() ; runners.save()

## helper functions

def txtindicts(result, d):
    """ return lowlevel values in (nested) dicts. """
    for j in d.values():
        if type(j) == types.DictType: txtindicts(result, j) 
        else: result.append(j)

def checkfordate(data, date):
    """ see if date is in data (list of feed items). """
    if not data: return False
    for item in data:
        try: d = item['updated']
        except (KeyError, TypeError): continue
        if date == d: return True
    return False

def find_self_url(links):
    for link in links:
        logging.debug("trying link: %s" % (strippassword(link)))
        if link.rel == 'self': return link.href
    return None

def strippassword(url):
    newurl = re.sub(r'^(https?://[^:/]*):([^@]*)@(\S+)$', r'\1:passwdblanked@\3', url)
    if newurl: return newurl
    return url

## Feed class

class Feed(Persist):

    """ item that contains rss data """

    def __init__(self, name="nonameset", url="", owner="noownerset", itemslist=['title', 'link'], watchchannels=[], \
sleeptime=15*60, running=0):
        if name:
            filebase = getdatadir() + os.sep + 'plugs' + os.sep + 'jsb.plugs.common.rss' + os.sep + name
            Persist.__init__(self, filebase + '-core')
            if not self.data: self.data = {}
            self.data = LazyDict(self.data)
            self.data.length = 200
            self.data['name'] = self.data.name or unicode(name)
            self.data['url'] = self.data.url or unicode(url)
            self.data['owner'] = self.data.owner or unicode(owner)
            self.data['result'] = []
            self.data['seen'] = self.data.seen or []
            self.data['watchchannels'] = self.data.watchchannels or list(watchchannels)
            self.data['running'] = self.data.running or running
            self.itemslists = Pdol(filebase + '-itemslists')
            self.markup = Pdod(filebase + '-markup')
        else: raise NameNotSet()

    def checkseen(self, data, itemslist=["title", "link"]):
        d = {}
        for item in itemslist:
            try: d[item] = data[item]
            except (KeyError, TypeError): continue
        digest = hashlib.md5(unicode(d)).hexdigest()
        return digest in self.data.seen

    def setseen(self, data, itemslist=['title', 'link'], length=200):
        d = {}
        for item in itemslist:
            d[item] = data[item]
        digest = hashlib.md5(unicode(d)).hexdigest()
        if digest not in self.data.seen: self.data.seen.insert(0, digest)
        self.data.seen = self.data.seen[:self.data.length]
        return self.data.seen

    def ownercheck(self, userhost):
        """ check is userhost is the owner of the feed. """
        try: return self.data.owner.lower() == userhost.lower()
        except KeyError: pass
        return False

    def save(self, coreonly=False):
        """ save rss data. """
        Persist.save(self)
        if not coreonly:
            self.itemslists.save()
            self.markup.save()

    def getdata(self):
        """ return data from cache or run fetchdata() to retrieve them. """
        url = self.data['url']
        result = get(url, namespace='rss')
        if result == None:
            result = self.fetchdata()
            set(url, result, namespace='rss')
            logging.debug("got result from %s" % strippassword(url))
        else: logging.debug("got result from %s *cached*" % strippassword(url))
        return result

    def fetchdata(self, data=None):
        """ get data of rss feed. """

        name = self.data.name
        global etags
        if name and etags.data.has_key(name): etag = etags.data[name]
        else: etag = None
        if data:
            result = feedparser.parse(data.content, etag=etag)
            try: status = data.status_code
            except AttributeError: status = None
        else:
            url = self.data['url']
            logging.info("fetching %s" % strippassword(url))
            result = feedparser.parse(url, agent=useragent(), etag=etag)
            try: status = result.status
            except AttributeError: status = None
        logging.info("status returned of %s feed is %s" % (name, status))
        if status == 304: return []
        if result: set(self.data.url, result.entries, namespace='rss')
        if data:
            try: etag = etags.data[name] = data.headers.get('etag') ; logging.info("etag of %s set to %s" % (name, etags.data[name])) ; etags.sync()
            except KeyError: etag = None
        else:
            try: etag = etags.data[name] = result.etag ; logging.info("etag of %s set to %s" % (name, etags.data[name])) ; etags.sync()
            except (AttributeError, KeyError): etag = None
        if not name in urls.data: urls.data[name] = self.data.url ; urls.save()
        logging.debug("got result from %s" % strippassword(self.data.url))
        if result and result.has_key('bozo_exception'): logging.debug('%s bozo_exception: %s' % (strippassword(self.data.url), result['bozo_exception']))
        l = len(result.entries)
        if l > self.data.length: self.data.length = l ; self.save()
        return result.entries

    def sync(self):
        """ refresh cached data of a feed. """
        if not self.data.running:
            logging.info("%s not enabled .. %s not syncing " % (self.data.name,strippassword( self.data.url)))
            return False
        logging.info("syncing %s - %s" % (self.data.name, strippassword(self.data.url)))
        result = self.fetchdata()
        if not result:
            cached = get(self.data.url, namespace="rss")
            if cached: result = cached
            else: result = []
        return result

    def check(self, entries=None, save=True):
        got = False
        tobereturned = []
        if entries == None: entries = self.fetchdata()
        if entries:
            for res in entries[::-1]:
                if self.checkseen(res): continue 
                tobereturned.append(LazyDict(res))
                got = True
                self.setseen(res)
            if got and save: self.save()
            logging.debug("%s - %s items ready" % (self.data.name, len(tobereturned)))
        return tobereturned

    def deliver(self, datalist, save=True):
        name = self.data.name
        try:
            loopover = self.data.watchchannels
            logging.info("loopover in %s deliver is: %s" % (self.data.name, loopover))
            for item in loopover:
                logging.info("item is: %s" % str(item))
                if not item: continue
                try:
                    (botname, type, channel) = item
                except ValueError:
                    logging.warn('%s is not in the format (botname, type, channel)' % str(item))
                    continue
                if not botname: logging.error("%s - %s is not correct" % (name, str(item))) ; continue
                if not type: logging.error("%s - %s is not correct" % (name, str(item))) ; continue
                try:
                    bot = getfleet().byname(botname)
                    if not bot: bot = getfleet().makebot(type, botname)
                except NoSuchBotType, ex: logging.warn("can't make bot - %s" % str(ex)) ; continue
                if not bot: logging.error("can't find %s bot in fleet" % botname) ; continue
                res2 = datalist
                if type == "irc" and not '#' in channel: nick = getwho(bot, channel)
                else: nick = None                        
                if self.markup.get(jsonstring([name, type, channel]), 'reverse-order'): res2 = res2[::-1]
                if self.markup.get(jsonstring([name, type, channel]), 'all-lines'):
                    for i in res2: 
                        response = self.makeresponse(name, type, [i, ], channel)
                        try: bot.saynocb(nick or channel, response, **{'headlines': True})
                        except Exception, ex: handle_exception()
                else:
                    sep =  self.markup.get(jsonstring([name, type, channel]), 'separator')
                    if sep: response = self.makeresponse(name, type, res2, channel, sep=sep)
                    else: response = self.makeresponse(name, type, res2, channel)
                    try: bot.saynocb(nick or channel, response, **{'headlines': True})
                    except Exception, ex: handle_exception()
            return True
        except Exception, ex: handle_exception(txt=name) ; return False

    def makeresponse(self, name, type, res, channel, sep=" || "):
        """ loop over result to make a response. """
        if self.markup.get(jsonstring([name, type, channel]), 'nofeedname'): result = u""
        else: result = u"<b>[%s]</b> - " % name 
        try: itemslist = self.itemslists.data[jsonstring([name, type, channel])]
        except KeyError:
            itemslist = self.itemslists.data[jsonstring([name, type, channel])] = ['title', 'link']
            self.itemslists.save()
        for j in res:
            if self.markup.get(jsonstring([name, type, channel]), 'skipmerge') and 'Merge branch' in j['title']: continue
            resultstr = u""
            for i in itemslist:
                try:
                    item = getattr(j, i)
                    if not item: continue
                    item = unicode(item)
                    if item.startswith('http://'):
                        if self.markup.get(jsonstring([name, type, channel]), 'tinyurl'):
                            try:
                                tinyurl = get_tinyurl(item)
                                logging.debug(' tinyurl is: %s' % str(tinyurl))
                                if not tinyurl: resultstr += u"%s - " % item
                                else: resultstr += u"%s - " % tinyurl[0]
                            except Exception, ex:
                                handle_exception()
                                resultstr += u"%s - " % item
                        else: resultstr += u"%s - " % item
                    else: resultstr += u"%s - " % item.strip()
                except (KeyError, AttributeError, TypeError), ex: logging.warn('%s - %s' % (name, str(ex))) ; continue
            resultstr = resultstr[:-3]
            if resultstr: result += u"%s %s " % (resultstr, sep)
        return result[:-(len(sep)+2)]

    def all(self):
        """ get all entries of the feed. """
        return self.getdata()

    def search(self, item, search):
        """ search feed entries. """
        res = []
        for result in self.all():
            try: i = getattr(result, item)
            except AttributeError: continue
            if i and search in i: res.append(i)
        return res

## Rssdict class

class Rssdict(PlugPersist):

    """ dict of rss entries """

    def __init__(self, filename, feedname=None):
        self.sleepsec = 900
        self.feeds = LazyDict()
        PlugPersist.__init__(self, filename)
        if not self.data:
            self.data = LazyDict()
            self.data['names'] = []
            self.data['urls'] = {}
        else:
            self.data = LazyDict(self.data)
            if not self.data.has_key('names'): self.data['names'] = []
            if not self.data.has_key('urls'): self.data['urls'] = {}
            if not feedname: pass
            else: self.feeds[feedname] = Feed(feedname)
        #self.startwatchers()

    def save(self, namein=None):
        """ save all feeds or provide a feedname to save. """
        PlugPersist.save(self)
        for name, feed in self.feeds.iteritems():
            if namein and name != namein: continue
            try: feed.save()
            except Exception, ex: handle_exception()

    def size(self):
        """ return number of rss feeds. """
        return len(self.data['names'])

    def add(self, name, url, owner):
        """ add rss item. """
        logging.warn('adding %s - %s - (%s)' % (name, strippassword(url), owner))
        if name not in self.data['names']: self.data['names'].append(name)
        self.feeds[name] = Feed(name, url, owner, ['title', 'link'])
        self.data['urls'][url] = name
        self.feeds[name].save()
        self.watch(name)
        self.save(name)

    def delete(self, name):
        """ delete rss item by name. """
        target = self.byname(name)
        if target:
            target.data.stoprunning = 1
            target.data.running = 0
            target.save()
            try: del self.feeds[name]
            except KeyError: pass
            try: self.data['names'].remove(name)
            except ValueError: pass
            self.save()

    def byname(self, name):
        """ return rss item by name. """
        if not name: return
        item = Feed(name)
        if item.data.url: return item 

    def cloneurl(self, url, auth):
        """ add feeds from remote url. """
        data = geturl2(url)
        got = []
        for line in data.split('\n'):
            try: (name, url) = line.split()
            except ValueError: logging.debug("cloneurl - can't split %s line" % line) ; continue
            if self.byname(name): logging.debug('cloneurl - already got %s feed' % name) ; continue
            if url.endswith('<br>'): url = url[:-4]
            self.add(name, url, auth)
            got.append(name)
        return got

    def getdata(self, name):
        """ get data of rss feed. """
        rssitem = self.byname(name)
        if rssitem == None: raise RssNoSuchItem("no %s rss item found" % name)
        return rssitem.getdata()

    def watch(self, name, sleepsec=900):
        """ start a watcher thread """
        logging.debug('trying %s rss feed watcher' % name)
        rssitem = self.byname(name)
        if rssitem == None: raise RssNoItem()
        rssitem.data.running = 1
        rssitem.data.stoprunning = 0
        res = rssitem.sync() 
        rssitem.check(res)
        rssitem.save()
        if not name in runners.data: runners.data[name] = "bla" ; runners.save()
        sleeptime.data[name] = sleepsec
        sleeptime.save()
        logging.warn('started %s rss watch' % name)

## Rsswatcher class

class Rsswatcher(Rssdict):

    """ rss watchers. """ 

    def checkfeed(self, url, event):
        """ get data of rss feed. """
        result = feedparser.parse(url, agent=useragent())
        logging.info("fetch - got result from %s" % strippassword(url))
        if result and result.has_key('bozo_exception'):
            event.reply('%s bozo_exception: %s' % (strippassword(url), result['bozo_exception']))
            return True
        try: status = result.status ; event.reply("%s - status is %s" % (strippassword(url), status))
        except AttributeError: status = 200
        if status != 200 and status != 301 and status != 302: return False
        return True

    def byurl(self, url):
        try: name = self.data['urls'][url]
        except KeyError: return
        return self.byname(name)

    def handle_data(self, data, name=None):
        """ handle data received in callback. """
        try:
            if name: rssitem = self.byname(name)
            else: url = find_self_url(result.feed.links) ; rssitem = self.byurl(url)
            if rssitem: name = rssitem.data.name
            else: logging.info("can't find %s item" % strippassword(url)) ; del data ; return
            if not name in urls.data: urls.data[name] = url ; urls.save()
            result = rssitem.fetchdata(data)
            logging.info("%s - got %s items from feed" % (name, len(result)))
            res = rssitem.check(result)
            if res: rssitem.deliver(res, save=True)
            else: logging.info("%s - no items to deliver" % name)
        except Exception, ex: handle_exception(txt=name)
        del data
        return True

    def getall(self):
        """ get all feeds. """
        for name in self.data['names']: self.feeds[name] = Feed(name)
        return self.feeds
       
    def shouldpoll(self, name, curtime):
        """ check whether poll of feed in needed. """
        return self.byname(name).shouldpoll(curtime)

    def get(self, name, userhost, save=True):
        """ get entries for a user. """
        return self.byname(name).get(userhost, save)

    def check(self, name, entries=None, save=True):
        """ check for updates. """
        return self.byname(name).check(entries=entries, save=save)

    def syncdeliver(self, name):
        """ sync a feed. """
        feed = self.byname(name)
        if feed:
            result = feed.sync()
            if result:
                res2 = feed.check(result)
                if res2: feed.deliver(res2)

    def ownercheck(self, name, userhost):
        """ check if userhost is the owner of feed. """
        try:
            feed = self.byname(name)
            if feed: return feed.ownercheck(userhost)
        except KeyError: pass
        return False

    def changeinterval(self, name, interval):
        """ not implemented yet. """
        sleeptime.data[name] = interval
        sleeptime.save()

    def stopwatchers(self):
        """ stop all watcher threads. """
        for j, z in self.data.iteritems():
            if z.data.running: z.data.stoprunning = 1

    def dowatch(self, name, sleeptime=1800):
        """ start a watcher. """
        rssitem = self.byname(name)
        if not rssitem == None:
            logging.error("no %s rss item available" % name)
            return
        while 1:
            try: self.watch(name)
            except Exception, ex:
                logging.warn('%s feed error: %s' % (name, str(ex)))
                if not rssitem.data.running: break
            else: break

    def stopwatch(self, name, save=True):
        """ stop watcher thread. """
        try:
            feed = self.byname(name)
            if feed:
                feed.data.running = 0
                feed.data.stoprunning = 1
                if save: feed.save()
        except KeyError: pass
        try:
             del runners.data[name]
             if save: runners.save()
             return True
        except KeyError: pass
        return False

    def list(self):
        """ return of rss names. """
        feeds = self.data['names']
        return feeds

    def runners(self):
        if runners.data: return runners.data.keys()
        return []

    def checkrunners(self):	
        """ show names/channels of running watchers. """
        result = []
        for name in self.data['names']:
            z = self.byname(name)
            if z and z.data.running == 1 and not z.data.stoprunning: 
                result.append((z.data.name, z.data.watchchannels))
                runners.data[name] = z.data.watchchannels
        runners.save()
        return result

    def getfeeds(self, botname, type, channel):
        """ show names/channels of running watcher. """
        result = []
        for name in self.runners():
            z = self.byname(name)
            if not z or not z.data.running: continue
            if jsonstring([botname, type, channel]) in z.data.watchchannels or [botname, type, channel] in z.data.watchchannels:
                result.append(z.data.name)
        return result

    def url(self, name):
        """ return url of rssitem. """
        return self.byname(name).data.url

    def seturl(self, name, url):
        """ set url of rssitem. """
        feed = self.byname(name)
        feed.data.url = url
        feed.save()
        return True

    def scan(self, name):
        """ scan a rss url for tokens. """
        keys = []
        items = self.byname(name).getdata()
        for item in items:
            for key in item:
                keys.append(key)         
        statdict = StatDict()
        for key in keys: statdict.upitem(key)
        return statdict.top()  

    def search(self, name, item, search):
        """ search titles of a feeds cached data. """
        i = self.byname(name)
        if i: return i.search(item, search)
        return []

    def searchall(self, item, search):
        """ search titles of all cached data. """
        res = []
        for name in self.data['names']:
            feed = self.byname(name)
            if feed: res.append(str(feed.search(item, search)))
        return res

    def all(self, name, item):
        """ search all cached data of a feed. """
        res = []
        feed = self.byname(name)
        if not feed: return res
        for result in feed.all():
            try: txt = getattr(result, item)
            except AttributeError: continue
            if txt: res.append(txt)
        return res

    def startwatchers(self):
        """ start watcher threads """
        for name in self.data['names']:
            z = self.byname(name)
            if z and z.data.running: self.watch(z.data.name)

    def start(self, botname, bottype, name, channel):
        """ start a rss feed (per user/channel). """
        rssitem = self.byname(name)
        if rssitem == None: logging.warn("we don't have a %s rss object" % name) ; return False
        target = channel
        if not jsonstring([botname, bottype, target]) in rssitem.data.watchchannels and not [botname, bottype, target] in rssitem.data.watchchannels:
            rssitem.data.watchchannels.append([botname, bottype, target])
        rssitem.itemslists[jsonstring([name, bottype, target])] = ['title', 'link']
        rssitem.markup.set(jsonstring([name, bottype, target]), 'tinyurl', 1)
        rssitem.data.running = 1
        rssitem.data.stoprunning = 0
        rssitem.save()
        if name not in self.runners(): watcher.watch(name)
        logging.warn("started %s feed in %s channel" % (name, channel))
        return True

    def stop(self, botname, bottype, name, channel):
        """ stop a rss feed (per user/channel). """
        rssitem = self.byname(name)
        if not rssitem: return False
        try:
            rssitem.data.watchchannels.remove([botname, bottype, channel])
            rssitem.save()
            logging.warn("stopped %s feed in %s channel" % (name, channel))
        except ValueError: return False
        return True

    def clone(self, botname, bottype, newchannel, oldchannel):
        """ clone feeds from one channel to another. """
        feeds = self.getfeeds(botname, oldchannel)
        for feed in feeds:
            self.stop(botname, bottype, feed, oldchannel)
            self.start(botname, bottype, feed, newchannel)
        return feeds

## more global defines 

watcher = Rsswatcher('rss')
urls = PlugPersist('urls')
etags = PlugPersist('etags')

assert(watcher)

## dosync function

def dummycb(bot, event): pass

callbacks.add('START', dummycb)


def dosync(feedname):
    """ main level function to be deferred by periodical. """
    try:
       logging.info("doing sync of %s" % feedname)
       localwatcher = Rsswatcher('rss', feedname)
       localwatcher.syncdeliver(feedname)
    except RssException, ex: logging.error("%s - error: %s" % (feedname, str(ex)))

## shouldpoll function

def shouldpoll(name, curtime):
    """ check whether a new poll is needed. """
    global lastpoll
    try: lp = lastpoll.data[name]
    except KeyError: lp = lastpoll.data[name] = time.time() ; lastpoll.sync()
    global sleeptime
    try: st = sleeptime.data[name]
    except KeyError: st = sleeptime.data[name] = 900 ; sleeptime.sync()
    logging.debug("pollcheck - %s - %s - remaining %s" % (name, time.ctime(lp), (lp + st) - curtime))
    if curtime - lp > st: return True

## dodata function

def dodata(data, name):
    watcher.handle_data(data, name=name)    

## rssfetchcb callback

def rssfetchcb(rpc):
    """ used on GAE todo a async fetch of the feeds. """
    import google
    try: data = rpc.get_result()
    except google.appengine.api.urlfetch_errors.DownloadError, ex: logging.warn("%s - error: %s" % (strippassword(rpc.final_url), str(ex))) ; return
    name = rpc.feedname
    logging.debug("headers of %s: %s" % (name, unicode(data.headers)))
    if data.status_code == 200:
        logging.info("defered %s feed" % rpc.feedname)
        from google.appengine.ext.deferred import defer
        defer(dodata, data, rpc.feedname)
    else: logging.info("fetch returned status code %s - %s" % (data.status_code, strippassword(rpc.feedurl)))

## creaete_rsscallback function

def create_rsscallback(rpc):
    """ return a callback for an rpc. """
    return lambda: rssfetchcb(rpc)

## doperiodicalGAE function

def doperiodicalGAE(*args, **kwargs):
    """ rss periodical function. """
    import google
    from google.appengine.api import urlfetch, urlfetch_errors
    curtime = time.time()
    feedstofetch = []
    rpcs = []
    for feed in watcher.runners():
        if not shouldpoll(feed, curtime): continue
        feedstofetch.append(feed)
    logging.info("feeds to fetch: %s" % str(feedstofetch))
    got = False
    for f in feedstofetch:
        if not f: continue
        lastpoll.data[f] = curtime
        if f not in urls.data: url = Feed(f).data.url ; urls.data[f] = url ; got = True
        else: url = urls.data[f]
        rpc = urlfetch.create_rpc()
        rpc.feedname = f
        rpc.callback = create_rsscallback(rpc)
        rpc.feedurl = url
        try: etag = etags.data[f]
        except KeyError: etag = ""
        logging.info("%s - sending request - %s" % (f, etag))
        try: urlfetch.make_fetch_call(rpc, url, headers={"If-None-Match": etag}) ; rpcs.append(rpc)
        except urlfetch_errors.InvalidURLError: logging.warn("%s url is invalid" % url) ; continue
        except Exception, ex: handle_exception()
    for rpc in rpcs: 
        try: rpc.wait()
        except google.appengine.api.urlfetch_errors.InvalidURLError, ex: logging.warn("url is invalid: %s" % str(ex))
        except Exception, ex: handle_exception()
    if feedstofetch: lastpoll.save()
    if got: urls.save()

## doperiodical function

def doperiodical(*args, **kwargs):
    """ rss periodical function. """
    curtime = time.time()
    for feed in watcher.data.names:
        if not shouldpoll(feed, curtime): continue
        lastpoll.data[feed] = curtime
        logging.debug("periodical - launching %s" % feed)
        try:
            from google.appengine.ext.deferred import defer
            defer(dosync, feed)
        except ImportError:
            try: start_new_thread(dosync, (feed, ))
            except Exception, ex: handle_exception() ; return
    lastpoll.save()

callbacks.add('TICK60', doperiodical)

## init function

def init():
    """ initialize the rss plugin. """
    taskmanager.add('rss', doperiodicalGAE)
    if not runners.data: watcher.checkrunners()
    
## shutdown function

def shutdown():
    """ shutdown the rss plugin. """
    taskmanager.unload('rss')

## size function

def size():
    """ return number of watched rss entries. """
    return watcher.size()

## save function

def save():
    """ save watcher data. """
    watcher.save()

## rss-clone command

def handle_rssclone(bot, event):
    """ arguments: <channel> - clone feed running in a channel. """
    if not event.rest: event.missing('<channel>') ; event.done()
    feeds = watcher.clone(bot.cfg.name, event.channel, event.rest)
    event.reply('cloned the following feeds: ', feeds)
 
cmnds.add('rss-clone', handle_rssclone, 'USER')
examples.add('rss-clone', 'clone feeds into new channel', 'wave-clone #dunkbots')

## rss-cloneurl command

def handle_rsscloneurl(bot, event):
    """ arguments: <url> - clone feeds from another bot (pointed to by url). """
    if not event.rest: event.missing('<url>') ; event.done
    feeds = watcher.cloneurl(event.rest, event.auth)
    event.reply('cloned the following feeds: ', feeds)
 
cmnds.add('rss-cloneurl', handle_rsscloneurl, 'OPER')
examples.add('rss-cloneurl', 'clone feeds from remote url', 'wave-clone jsonbot-hg http://jsonbot.appspot.com')

## rss-add command

def handle_rssadd(bot, ievent):
    """ arguments: <feedname> <url> - add a rss item. """
    try: (name, url) = ievent.args
    except ValueError: ievent.missing('<feedname> <url>') ; return
    if watcher.checkfeed(url, ievent): watcher.add(name, url, ievent.userhost) ; ievent.reply('rss item added')
    else: ievent.reply('%s is not valid' % strippassword(url))

cmnds.add('rss-add', handle_rssadd, 'USER')
examples.add('rss-add', 'add a feed to the rsswatcher', 'rss-add jsonbot http://code.google.com/feeds/p/jsonbot/hgchanges/basic')

## rss-register command

def handle_rssregister(bot, ievent):
    """ arguments: <feedname> <url> - register and start a rss item. """
    try: (name, url) = ievent.args
    except ValueError: ievent.missing('<feedname> <url>') ; return
    if watcher.byname(name):
        ievent.reply('we already have a feed with %s name .. plz choose a different name' % name)
        return
    if watcher.checkfeed(url, ievent):
        watcher.add(name, url, ievent.userhost)
        watcher.start(bot.cfg.name, bot.type, name, ievent.channel)
        if name not in ievent.chan.data.feeds: ievent.chan.data.feeds.append(name) ; ievent.chan.save()
        ievent.reply('rss item added and started in channel %s' % ievent.channel)
    else: ievent.reply('%s is not valid' % strippassword(url))

cmnds.add('rss-register', handle_rssregister, 'USER')
examples.add('rss-register', 'register and start a rss feed', 'rss-register jsonbot-hg http://code.google.com/feeds/p/jsonbot/hgchanges/basic')

## rss-del command

def handle_rssdel(bot, ievent):
    """ arguments: <feedname> .. delete a rss item. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    rssitem =  watcher.byname(name)
    if rssitem:
        if not watcher.ownercheck(name, ievent.userhost): ievent.reply("you are not the owner of the %s feed" % name) ; return
        watcher.stopwatch(name)
        watcher.delete(name)
        ievent.reply('rss item deleted')
    else: ievent.reply('there is no %s rss item' % name)

cmnds.add('rss-del', handle_rssdel, ['USER', ])
examples.add('rss-del', 'remove a feed from the rsswatcher', 'rss-del mekker')

## rss-sync command

def handle_rsssync(bot, ievent):
    """ arguments: <feedname> - sync a feed with the latest. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    if name in watcher.data['names']: watcher.byname(name).sync() ; ievent.done()
    else: ievent.reply("no %s feed available" % name)

cmnds.add('rss-sync', handle_rsssync, ['OPER', ])
examples.add('rss-sync', 'sync feed with the latest.', 'rss-sync mekker')

## rss-watch command

def handle_rsswatch(bot, ievent):
    """ arguments: <feedname> [secondstosleep] - start watching a feed. """
    try: name, sleepsec = ievent.args
    except ValueError:
        try: name = ievent.args[0] ; sleepsec = 1800
        except IndexError: ievent.missing('<feedname> [secondstosleep]') ; return
    try: sleepsec = int(sleepsec)
    except ValueError: ievent.reply("time to sleep needs to be in seconds") ; return
    if name == "all": target = watcher.data.names
    else: target = [name, ]
    got = []
    for feed in target:
        rssitem = watcher.byname(feed)
        if rssitem == None: continue
        if not sleeptime.data.has_key(name): sleeptime.data[feed] = sleepsec ; sleeptime.save()
        try: watcher.watch(feed, sleepsec)
        except Exception, ex: ievent.reply('%s - %s' % (feed, str(ex))) ; continue
        got.append(feed)
    if got: ievent.reply('watcher started ', got)
    else: ievent.reply('already watching ', target)


cmnds.add('rss-watch', handle_rsswatch, 'USER')
examples.add('rss-watch', 'start watching a feed', '1) rss-watch jsonbot 2) rss-watch jsonbot 600')

## rss-start command

def handle_rssstart(bot, ievent):
    """ arguments: <list of feeds|"all"> - start a rss feed to a user/channel. """
    feeds = ievent.args
    if not feeds: ievent.missing('<list of feeds>') ; return
    started = []
    if feeds[0] == 'all': feeds = watcher.list()
    if ievent.options and ievent.options.channel: target = ievent.options.channel
    else: target = ievent.channel
    for name in feeds:
        watcher.start(bot.cfg.name, bot.type, name, target)
        started.append(name)
    for chan in started:
        tchan = ChannelBase(target)
        if name not in tchan.data.feeds: tchan.data.feeds.append(name) ; tchan.save()
    ievent.reply('started: ', started)

cmnds.add('rss-start', handle_rssstart, ['RSS', 'USER'])
examples.add('rss-start', 'start a rss feed (per user/channel) ', 'rss-start jsonbot')

## rss-stop command

def handle_rssstop(bot, ievent):
    """ arguments: <feedname> .. stop a rss feed to a user/channel. """
    if not ievent.rest: ievent.missing('<feedname>') ; return
    if ievent.rest == "all": loopover = ievent.chan.data.feeds
    else: loopover = [ievent.rest, ]
    stopped = []
    for name in loopover:
        if name in ievent.chan.data.feeds: ievent.chan.data.feeds.remove(name) 
        rssitem = watcher.byname(name)
        target = ievent.channel
        if rssitem == None: continue
        if not rssitem.data.running: continue
        try: rssitem.data.watchchannels.remove([bot.cfg.name, bot.type, target])
        except ValueError:
            try: rssitem.data.watchchannels.remove([bot.cfg.name, bot.type, target])
            except ValueError: continue
        rssitem.save()
        stopped.append(name)
    ievent.chan.save()
    ievent.reply('stopped feeds: ', stopped)

cmnds.add('rss-stop', handle_rssstop, ['RSS', 'USER'])
examples.add('rss-stop', 'stop a rss feed (per user/channel) ', 'rss-stop jsonbot')

## rss-stopall command

def handle_rssstopall(bot, ievent):
    """ no arguments - stop all rss feeds to a channel. """
    if not ievent.rest: target = ievent.channel
    else: target = ievent.rest
    stopped = []
    feeds = watcher.getfeeds(bot.cfg.name, bot.type, target)
    if feeds:
        for feed in feeds:
            if watcher.stop(bot.cfg.name, bot.type, feed, target):
                if feed in ievent.chan.data.feeds: ievent.chan.data.feeds.remove(feed) ; ievent.chan.save()
                stopped.append(feed)
        ievent.reply('stopped feeds: ', stopped)
    else: ievent.reply('no feeds running in %s' % target)

cmnds.add('rss-stopall', handle_rssstopall, ['RSS', 'OPER'])
examples.add('rss-stopall', 'rss-stopall .. stop all rss feeds (per user/channel) ', 'rss-stopall')

## rss-channels command

def handle_rsschannels(bot, ievent):
    """ arguments: <feedname> - show channels of rss feed. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing("<feedname>")  ; return
    rssitem = watcher.byname(name)
    if rssitem == None: ievent.reply("we don't have a %s rss object" % name) ; return
    if not rssitem.data.watchchannels: ievent.reply('%s is not in watch mode' % name) ; return
    result = []
    for i in rssitem.data.watchchannels: result.append(str(i))
    ievent.reply("channels of %s: " % name, result)

cmnds.add('rss-channels', handle_rsschannels, ['OPER', ])
examples.add('rss-channels', 'show channels in which a feed runs', 'rss-channels jsonbot')

## rss-addchannel command

def handle_rssaddchannel(bot, ievent):
    """ arguments: <feedname> [<botname>] [<bottype>] [<channel>] - add a channel to rss item. """
    try: (name, botname, type, channel) = ievent.args
    except ValueError:
        try: (name, channel) = ievent.args ; botname = bot.cfg.name ; type = bot.type
        except ValueError:
            try: name = ievent.args[0] ; botname = bot.cfg.name ; type = bot.type ; channel = ievent.channel
            except IndexError: ievent.missing('<feedname> [<botname>] [<bottype] [<channel>]') ; return
    rssitem = watcher.byname(name)
    if rssitem == None: ievent.reply("we don't have a %s rss object" % name) ; return
    if not rssitem.data.running: ievent.reply('%s watcher is not running' % name) ; return
    if jsonstring([botname, type, channel]) in rssitem.data.watchchannels or [botname, channel] in rssitem.data.watchchannels:
        ievent.reply('we are already monitoring %s on (%s,%s)' % (name, botname, channel))
        return
    rssitem.data.watchchannels.append([botname, type, channel])
    rssitem.save()
    ievent.reply('%s added to %s rss item' % (channel, name))

cmnds.add('rss-addchannel', handle_rssaddchannel, ['OPER', ])
examples.add('rss-addchannel', 'add a channel to watchchannels of a feed', '1) rss-addchannel jsonbot #dunkbots 2) rss-addchannel jsonbot main #dunkbots')

## rss-setitems command

def handle_rsssetitems(bot, ievent):
    """ arguments: <feedname> <tokens> - set tokens to display - see rss-scan for available tokens. """
    try: (name, items) = ievent.args[0], ievent.args[1:]
    except (ValueError, IndexError): ievent.missing('<feedname> <list of tokens>') ; return
    if ievent.options and ievent.options.channel: target = ievent.options.channel
    else: target = ievent.channel
    rssitem = watcher.byname(name)
    if not rssitem: ievent.reply("we don't have a %s feed" % name) ; return
    rssitem.itemslists.data[jsonstring([name, bot.type, target])] = items
    rssitem.itemslists.save()
    ievent.reply('%s added to (%s,%s) itemslist' % (items, name, target))

cmnds.add('rss-setitems', handle_rsssetitems, ['RSS', 'USER'])
examples.add('rss-setitems', 'set tokens of the itemslist (per user/channel)', 'rss-setitems jsonbot author author link pubDate')

## rss-additem command

def handle_rssadditem(bot, ievent):
    """ arguments: <feedname> <token> - add an item (token) to a feeds tokens to be displayed, see rss-scan for a list of available tokens. """
    try: (name, item) = ievent.args
    except ValueError: ievent.missing('<feedname> <token>') ; return
    if ievent.options and ievent.options.channel: target = ievent.options.channel
    else: target = ievent.channel
    feed = watcher.byname(name)
    if not feed: ievent.reply("we don't have a %s feed" % name) ; return
    try: feed.itemslists.data[jsonstring([name, bot.type, target])].append(item)
    except KeyError: feed.itemslists.data[jsonstring([name, bot.type, target])] = ['title', 'link']
    feed.itemslists.save()
    ievent.reply('%s added to (%s,%s) itemslist' % (item, name, target))

cmnds.add('rss-additem', handle_rssadditem, ['RSS', 'USER'])
examples.add('rss-additem', 'add a token to the itemslist (per user/channel)', 'rss-additem jsonbot link')

## rss-delitem command

def handle_rssdelitem(bot, ievent):
    """ arguments: <feedname> <token> - delete token from a feeds itemlist. """
    try: (name, item) = ievent.args
    except ValueError: ievent.missing('<feedname> <token>') ; return
    if ievent.options and ievent.options.channel: target = ievent.options.channel
    else: target = ievent.channel
    rssitem =  watcher.byname(name)
    if not rssitem: ievent.reply("we don't have a %s feed" % name) ; return
    try:
        rssitem.itemslists.data[jsonstring([name, bot.type, target])].remove(item)
        rssitem.itemslists.save()
    except (ValueError, KeyError): ievent.reply("we don't have a %s rss feed" % name) ; return
    ievent.reply('%s removed from (%s,%s) itemslist' % (item, name, target))

cmnds.add('rss-delitem', handle_rssdelitem, ['RSS', 'USER'])
examples.add('rss-delitem', 'remove a token from the itemslist (per user/channel)', 'rss-delitem jsonbot link')

## rss-markuplist command

def handle_rssmarkuplist(bot, ievent):
    """ no arguments - show possible markups that can be used. """
    ievent.reply('possible markups ==> ' , possiblemarkup)

cmnds.add('rss-markuplist', handle_rssmarkuplist, ['USER', ])
examples.add('rss-markuplist', 'show possible markup entries', 'rss-markuplist')

## rss-markup command

def handle_rssmarkup(bot, ievent):
    """ arguments: <feedname> - show the markup of a feed. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    rssitem =  watcher.byname(name)
    if not rssitem: ievent.reply("we don't have a %s feed" % name) ; return
    if ievent.options and ievent.options.channel: target = ievent.options.channel
    else: target = ievent.channel
    try: ievent.reply(str(rssitem.markup[jsonstring([name, bot.type, target])]))
    except KeyError: pass

cmnds.add('rss-markup', handle_rssmarkup, ['RSS', 'USER'])
examples.add('rss-markup', 'show markup list for a feed (per user/channel)', 'rss-markup jsonbot')

## rss-addmarkup command

def handle_rssaddmarkup(bot, ievent):
    """ arguments: <feedname> <item> <value> - add a markup to a feeds markuplist. """
    try: (name, item, value) = ievent.args
    except ValueError: ievent.missing('<feedname> <item> <value>') ; return
    rssitem =  watcher.byname(name)
    if not rssitem: ievent.reply("we don't have a %s feed" % name) ; return
    if ievent.options and ievent.options.channel: target = ievent.options.channel
    else: target = ievent.channel
    try: value = int(value)
    except ValueError: pass
    try:
        rssitem.markup.set(jsonstring([name, bot.type, target]), item, value)
        rssitem.markup.save()
        ievent.reply('%s added to (%s,%s) markuplist' % (item, name, target))
    except KeyError: ievent.reply("no (%s,%s) feed available" % (name, target))

cmnds.add('rss-addmarkup', handle_rssaddmarkup, ['RSS', 'USER'])
examples.add('rss-addmarkup', 'add a markup option to the markuplist (per user/channel)', 'rss-addmarkup jsonbot all-lines 1')

## rss-delmarkup command

def handle_rssdelmarkup(bot, ievent):
    """ arguments: <feedname> <item> - delete markup from a feeds markuplist. """
    try: (name, item) = ievent.args
    except ValueError: ievent.missing('<feedname> <item>') ; return
    rssitem =  watcher.byname(name)
    if not rssitem: ievent.reply("we don't have a %s feed" % name) ; return
    if ievent.options and ievent.options.channel: target = ievent.options.channel
    else: target = ievent.channel
    try: del rssitem.markup[jsonstring([name, bot.type, target])][item]
    except (KeyError, TypeError): ievent.reply("can't remove %s from %s feed's markup" %  (item, name)) ; return
    rssitem.markup.save()
    ievent.reply('%s removed from (%s,%s) markuplist' % (item, name, target))

cmnds.add('rss-delmarkup', handle_rssdelmarkup, ['RSS', 'USER'])
examples.add('rss-delmarkup', 'remove a markup option from the markuplist (per user/channel)', 'rss-delmarkup jsonbot all-lines')

## rss-delchannel command

def handle_rssdelchannel(bot, ievent):
    """arguments: <feedname> [<botname>] [<bottype>] [<channel>] - delete channel from feed. """
    botname = None
    try: (name, botname, type, channel) = ievent.args
    except ValueError:
        try: (name, channel) = ievent.args ; type = bot.type ; botname = bot.cfg.name
        except ValueError:
            try:
                name = ievent.args[0]
                botname = bot.cfg.name
                type = bot.type
                channel = ievent.channel
            except IndexError: ievent.missing('<feedname> [<botname>] [<channel>]') ; return
    rssitem = watcher.byname(name)
    if rssitem == None: ievent.reply("we don't have a %s rss object" % name) ; return
    if jsonstring([botname, type, channel]) in rssitem.data.watchchannels:
        rssitem.data.watchchannels.remove(jsonstring([botname, type, channel]))
        ievent.reply('%s removed from %s rss item' % (channel, name))
    elif [botname, type, channel] in rssitem.data.watchchannels:
        rssitem.data.watchchannels.remove([botname, type, channel])
        ievent.reply('%s removed from %s rss item' % (channel, name))
    else: ievent.reply('we are not monitoring %s on (%s,%s)' % (name, botname, channel)) ; return
    rssitem.save()

cmnds.add('rss-delchannel', handle_rssdelchannel, ['OPER', ])
examples.add('rss-delchannel', 'delete channel from feed', '1) rss-delchannel jsonbot #dunkbots 2) rss-delchannel jsonbot main #dunkbots')

## rss-stopwatch command

def handle_rssstopwatch(bot, ievent):
    """ arguments: <feedname> - stop watching a feed. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    stopped = []
    if name == "all":
        for name in watcher.runners():
            if watcher.stopwatch(name): stopped.append(name)
    else:
        if watcher.stopwatch(name): stopped.append(name)
    ievent.reply('stopped rss watchers: ', stopped)

cmnds.add('rss-stopwatch', handle_rssstopwatch, ['OPER', ])
examples.add('rss-stopwatch', 'stop polling a feed', 'rss-stopwatch jsonbot')

## rss-sleeptime command

def handle_rsssleeptime(bot, ievent):
    """ arguments: <feedname> - get sleeptime of rss item. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    try: ievent.reply('sleeptime for %s is %s seconds' % (name, str(sleeptime.data[name])))
    except KeyError: ievent.reply("can't get sleeptime for %s" % name)

cmnds.add('rss-sleeptime', handle_rsssleeptime, 'USER')
examples.add('rss-sleeptime', 'get sleeping time of a feed', 'rss-sleeptime jsonbot')

## rss-setsleeptime command

def handle_rsssetsleeptime(bot, ievent):
    """ arguments: <feedname> <seconds> - set sleeptime of feed, minimum is 60 seconds. """
    try: (name, sec) = ievent.args ; sec = int(sec)
    except ValueError: ievent.missing('<name> <seconds>') ; return
    if not watcher.ownercheck(name, ievent.userhost): ievent.reply("you are not the owner of the %s feed" % name) ; return
    if sec < 60: ievent.reply('min is 60 seconds') ; return
    rssitem = watcher.byname(name)
    if rssitem == None: ievent.reply("we don't have a %s rss item" % name) ; return
    rssitem.data.sleeptime = sec
    if rssitem.data.running:
        try: watcher.changeinterval(name, sec)
        except KeyError, ex: ievent.reply("failed to set interval: %s" % str(ex)) ; return
    ievent.reply('sleeptime set')

cmnds.add('rss-setsleeptime', handle_rsssetsleeptime, ['USER', ])
examples.add('rss-setsleeptime', 'set sleeping time of a feed .. min 60 sec', 'rss-setsleeptime jsonbot 600')

## rss-get command

def handle_rssget(bot, ievent):
    """ arguments: <feedname> - fetch feed data. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    channel = ievent.channel
    rssitem = watcher.byname(name)
    if rssitem == None: ievent.reply("we don't have a %s rss item" % name) ; return
    try: result = watcher.getdata(name)
    except Exception, ex: ievent.reply('%s error: %s' % (name, str(ex))) ; return
    if rssitem.markup.get(jsonstring([name, bot.type, channel]), 'reverse-order'): result = result[::-1]
    response = rssitem.makeresponse(name, bot.type, result, ievent.channel)
    if response: ievent.reply("results of %s: %s" % (name, response))
    else: ievent.reply("can't make a reponse out of %s" % name)

cmnds.add('rss-get', handle_rssget, ['RSS', 'USER'], threaded=True)
examples.add('rss-get', 'get data of a feed', 'rss-get jsonbot')

## rss-running command

def handle_rssrunning(bot, ievent):
    """ no arguments - show which watchers are running. """
    result = watcher.runners()
    resultlist = []
    teller = 1
    for i in result: resultlist.append(i)
    if resultlist: ievent.reply("running rss watchers: ", resultlist)
    else: ievent.reply('nothing running yet')

cmnds.add('rss-running', handle_rssrunning, ['RSS', 'USER'])
examples.add('rss-running', 'rss-running .. get running rsswatchers', \
'rss-running')

## rss-list command

def handle_rsslist(bot, ievent):
    """ no arguments - return list of available rss items. """
    result = watcher.list()
    result.sort()
    if result: ievent.reply("rss items: ", result)
    else: ievent.reply('no rss items yet')

cmnds.add('rss-list', handle_rsslist, ['RSS', 'USER'])
examples.add('rss-list', 'get list of rss items', 'rss-list')

## rss-url command

def handle_rssurl(bot, ievent):
    """ arguments: <feedname> - return url of feed. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    if not watcher.ownercheck(name, ievent.userhost): ievent.reply("you are not the owner of the %s feed" % name) ; return
    result = watcher.url(name)
    if not result: ievent.reply("don't know url for %s" % name) ; return
    ievent.reply('url of %s: %s' % (name, strippassword(result)))

cmnds.add('rss-url', handle_rssurl, ['OPER', ])
examples.add('rss-url', 'get url of feed', 'rss-url jsonbot')

## rss-seturl command

def handle_rssseturl(bot, ievent):
    """ arguments: <feedname> <url> - set url of feed. """
    try: name = ievent.args[0] ; url = ievent.args[1]
    except IndexError: ievent.missing('<feedname> <url>') ; return
    if not watcher.ownercheck(name, ievent.userhost): ievent.reply("you are not the owner of the %s feed" % name) ; return
    oldurl = watcher.url(name)
    if not oldurl: ievent.reply("no %s rss item found" % name) ; return
    if watcher.seturl(name, url):
        rssitem = watcher.byname(name)
        rssitem.sync()
        ievent.reply('url of %s changed' % name)
    else: ievent.reply('failed to set url of %s to %s' % (name, strippassword(url)))

cmnds.add('rss-seturl', handle_rssseturl, ['USER', ])
examples.add('rss-seturl', 'set the url of a feed', 'rss-seturl jsonbot-hg http://code.google.com/feeds/p/jsonbot/hgchanges/basic')

## rss-itemslist

def handle_rssitemslist(bot, ievent):
    """ argumetns <feedname> - show list of tokens of feed that are being displayed. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('feed<name>') ; return
    rssitem = watcher.byname(name)
    if not rssitem: ievent.reply("we don't have a %s feed." % name) ; return
    if ievent.options and ievent.options.channel: target = ievent.options.channel
    else: target = ievent.channel
    try: itemslist = rssitem.itemslists[jsonstring([name, bot.type, target])]
    except KeyError: ievent.reply("no itemslist set for (%s, %s)" % (name, target)) ; return
    ievent.reply("itemslist of (%s, %s): " % (name, target), itemslist)

cmnds.add('rss-itemslist', handle_rssitemslist, ['RSS', 'USER'])
examples.add('rss-itemslist', 'get itemslist of feed', 'rss-itemslist jsonbot')

## rss-scan command

def handle_rssscan(bot, ievent):
    """ arguments: <feedname> - scan rss item for used xml tokens. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    if not watcher.byname(name): ievent.reply('no %s feeds available' % name) ; return
    try: result = watcher.scan(name)
    except Exception, ex: ievent.reply(str(ex)) ; return
    if result == None: ievent.reply("can't get data for %s" % name) ; return
    res = []
    for i in result: res.append("%s=%s" % i)
    ievent.reply("tokens of %s: " % name, res)

cmnds.add('rss-scan', handle_rssscan, ['USER', ])
examples.add('rss-scan', 'get possible tokens of a feed that can be displayed ', 'rss-scan jsonbot')

## rss-feeds

def handle_rssfeeds(bot, ievent):
    """ arguments: [<channel>] - show what feeds are running in a channel. """
    if ievent.options and ievent.options.channel: target = ievent.options.channel
    else: target = ievent.channel
    result = watcher.getfeeds(bot.cfg.name, bot.type, target)
    if result: ievent.reply("feeds running in %s: " % target, result)
    else: ievent.reply('%s has no feeds running' % target)

cmnds.add('rss-feeds', handle_rssfeeds, ['USER', 'RSS'])
examples.add('rss-feeds', 'show what feeds are running in a channel', '1) rss-feeds 2) rss-feeds #dunkbots')

## rss-link command

def handle_rsslink(bot, ievent):
    """ arguments: <feedname> <searchtxt> - search link entries in cached data. """
    try: feed, rest = ievent.rest.split(' ', 1)
    except ValueError: ievent.missing('<feedname> <searchtxt>') ; return
    rest = rest.strip().lower()
    try:
        res = watcher.search(feed, 'link', rest)
        if not res: res = watcher.search(feed, 'feedburner:origLink', rest)
        if res: ievent.reply("link: ", res, dot=" \002||\002 ")
    except KeyError: ievent.reply('no %s feed data available' % feed) ; return

cmnds.add('rss-link', handle_rsslink, ['RSS', 'USER'])
examples.add('rss-link', 'give link of feeds which title matches search key', 'rss-link jsonbot gozer')

## rss-description commmand

def handle_rssdescription(bot, ievent):
    """ arguments: <feedname> <searchtxt> - search descriptions in cached data. """
    try: feed, rest = ievent.rest.split(' ', 1)
    except ValueError: ievent.missing('<feedname> <searchtxt>') ; return
    rest = rest.strip().lower()
    res = ""
    try: ievent.reply("results: ", watcher.search(feed, 'summary', rest))
    except KeyError: ievent.reply('no %s feed data available' % feed) ; return

cmnds.add('rss-description', handle_rssdescription, ['RSS', 'USER'])
examples.add('rss-description', 'give description of item which title matches search key', 'rss-description jsonbot gozer')

## rss-all command

def handle_rssall(bot, ievent):
    """ arguments: <feedname> - search titles of all cached data of a feed. """
    try: feed = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    try: ievent.reply('results: ', watcher.all(feed, 'title'), dot=" \002||\002 ")
    except KeyError: ievent.reply('no %s feed data available' % feed) ; return

cmnds.add('rss-all', handle_rssall, ['RSS', 'USER'])
examples.add('rss-all', "give titles of a feed", 'rss-all jsonbot')

## rss-search

def handle_rsssearch(bot, ievent):
    """ arguments: <searchtxt> - search in titles of cached data. """
    try: txt = ievent.args[0]
    except IndexError: ievent.missing('<searchtxt>') ; return
    try: ievent.reply("results: ", watcher.searchall('title', txt))
    except KeyError: ievent.reply('no %s feed data available' % feed) ; return

cmnds.add('rss-search', handle_rsssearch, ['RSS', 'USER'])
examples.add('rss-search', "search titles of all current feeds", 'rss-search json')

def handle_rssimport(bot, ievent):
    """ arguments: <url> - import feeds uses OPML. """
    if not ievent.rest: ievent.missing("<url>") ; return
    import xml.etree.ElementTree as etree
    try:
        data = geturl2(ievent.rest)
        if not data: ievent.reply("can't fetch data from %s" % ievent.rest)
    except Exception, ex: ievent.reply("error fetching %s: %s" % (ievent.rest, str(ex))) ; return
    try: element = etree.fromstring(data)
    except Exception, ex: ievent.reply("error reading %s: %s" % (ievent.rest, str(ex))) ; return
    teller = 0
    errors = {}
    for elem in element.getiterator():
        name = elem.get("keyname") or elem.get("text")
        if name: name = "+".join(name.split())
        url = elem.get('url') or elem.get("xmlUrl")
        try:
            assert(name)
            assert(url)
            logging.warn("import - adding %s - %s" % (name, strippassword(url)))
            watcher.add(fromenc(name), fromenc(url), ievent.userhost)
            teller += 1
        except Exception, ex:
            errors[name] = str(ex)
    ievent.reply("added %s items" % teller)
    if errors:
        errlist = []
        for name, err in errors.iteritems():
            errlist.append("%s - %s" % (name, err))
        ievent.reply("there were errors: ", errlist)

cmnds.add('rss-import', handle_rssimport, ['OPER', ])
examples.add('rss-import', 'import rss feeds from a remote OPML file.', 'rss-import http://jsonbot.org/feeds.opml')
