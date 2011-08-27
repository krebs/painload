# jsb/plugs/common/hubbub.py
#
#

""" 
    the hubbub mantra is of the following:
    use the hb-register <feedname> <url> command to register url and start a feed in in one pass.

"""

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.persist import Persist, PlugPersist
from jsb.utils.pdol import Pdol
from jsb.utils.pdod import Pdod
from jsb.utils.generic import jsonstring
from jsb.utils.lazydict import LazyDict
from jsb.utils.url import useragent, geturl2
from jsb.utils.statdict import StatDict
from jsb.utils.exception import handle_exception
from jsb.lib.fleet import getfleet
from jsb.lib.channelbase import ChannelBase
from jsb.utils.url import posturl
from jsb.lib.errors import NoSuchBotType
from jsb.lib.threads import start_new_thread
from jsb.lib.datadir import getdatadir
from jsb.lib.jsbimport import _import_byfile
from jsb.imports import getfeedparser
feedparser = getfeedparser()

## basic imports

import base64
import logging
import urllib
import urlparse
import uuid
import os
import time

## subscribe function

def subscribe(url):
    """ subscribe to an hubbub feed. """
    subscribe_args = {
        'hub.callback': urlparse.urljoin('https://jsonbot.appspot.com', '/hubbub'),
        'hub.mode': 'subscribe',
        'hub.topic': url,
        'hub.verify': 'async',
        'hub.verify_token': str(uuid.uuid4()),
    }
    headers = {}
    credentials = _import_byfile("credentials", getdatadir() + os.sep + "config" + os.sep + "credentials.py")
    if credentials.HUB_CREDENTIALS:
      auth_string = "Basic " + base64.b64encode("%s:%s" % tuple(credentials.HUB_CREDENTIALS))
      headers['Authorization'] = auth_string
    logging.warn("hubbub - subscribe - trying %s (%s)" % (credentials.HUB_URL, url))
    logging.warn("hubbub - subscribe - %s" % str(headers))
    response = posturl(credentials.HUB_URL, headers, subscribe_args)
    return response

## tinyurl import

try:
    from jsb.plugs.common.tinyurl import get_tinyurl
except ImportError:
    def get_tinyurl(url):
        return [url, ]

## defines

allowedtokens = ['updated', 'link', 'summary', 'tags', 'author', 'content', 'title', 'subtitle']
savelist = []
possiblemarkup = {'separator': 'set this to desired item separator', \
'all-lines': "set this to 1 if you don't want items to be aggregated", \
'tinyurl': "set this to 1 when you want to use tinyurls", 'skipmerge': \
"set this to 1 if you want to skip merge commits", 'reverse-order': 'set \
this to 1 if you want the items displayed with oldest item first'}

def find_self_url(links):
    """ find home url of feed. """
    for link in links:
        if link.rel == 'self': return link.href

## NoSuchFeed exception

class NoSuchFeed(Exception):
    """ there is no such feed in the feed database. """
    pass

## HubbubItem class

class HubbubItem(Persist):

    """ item that contains hubbub data """


    def __init__(self, name, url="", owner="", itemslist=['title', 'link'], watchchannels=[], running=1):
        filebase = getdatadir() + os.sep + 'plugs' + os.sep + 'jsb.plugs.wave.hubbub' + os.sep + name
        Persist.__init__(self, filebase + os.sep + name + '.core')
        if not self.data: self.data = {}
        self.data = LazyDict(self.data)
        self.data['name'] = self.data.name or str(name)
        self.data['url'] = self.data.url or str(url)
        self.data['owner'] = self.data.owner or str(owner)
        self.data['watchchannels'] = self.data.watchchannels or list(watchchannels)
        self.data['running'] = self.data.running or running
        self.itemslists = Pdol(filebase + os.sep + name + '.itemslists')
        self.markup = Pdod(filebase + os.sep + name + '.markup')

    def save(self):
        """ save the hubbub items data. """
        Persist.save(self)
        self.itemslists.save()
        self.markup.save()

    def ownercheck(self, userhost):
        """ check is userhost is the owner of the feed. """
        try: return self.data.owner == userhost
        except KeyError: pass
        return False

    def fetchdata(self):
        """ get data of rss feed. """
        url = self.data['url']
        if not url:
            logging.warn("hubbub - %s doesnt have url set" % self.data.name)
            return []
        result = feedparser.parse(url, agent=useragent())
        logging.debug("hubbub - fetch - got result from %s" % url)
        if result and result.has_key('bozo_exception'): logging.info('hubbub - %s bozo_exception: %s' % (url, result['bozo_exception']))
        try:
            status = result.status
            logging.info("hubbub - status is %s" % status)
        except AttributeError: status = 200
        if status != 200 and status != 301 and status != 302: raise RssStatus(status)
        return result.entries

## HubbubWatcher class

class HubbubWatcher(PlugPersist):

    """ 
        this watcher helps with the handling of incoming POST. also maitains 
        index of feed names.
    """

    def __init__(self, filename):
        PlugPersist.__init__(self, filename)
        if not self.data: self.data = {}
        if not self.data.has_key('names'): self.data['names'] = []
        if not self.data.has_key('urls'): self.data['urls'] = {}
        if not self.data.has_key('feeds'): self.data['feeds'] = {}
        self.feeds = {}

    def add(self, name, url, owner):
        """ add a feed to the database. """
        if not name in self.data['names']:
            self.data['names'].append(name)
            self.data['urls'][url] = name
            self.save()

        item = HubbubItem(name, url, owner)
        if item.data.url != url:
            return False

        item.save()
        self.feeds[name] = item
        return True

    def byname(self, name):
        """ retrieve a feed by it's name. """
        if name in self.feeds: return self.feeds[name]
        item = HubbubItem(name)
        if item.data.url: self.feeds[name] = item ; return item

    def byurl(self, url):
        """ retrieve a feed by it's url. """
        try:
            name = self.data['urls'][url]
            return self.byname(name)
        except KeyError: pass

    def cloneurl(self, url, auth):
        """ add feeds from remote url. """
        data = geturl2(url)
        got = []
        for line in data.split('\n'):
            try: (name, url) = line.split()
            except ValueError:
                logging.debug("hubbub - cloneurl - can't split %s line" % line)
                continue
            if url.endswith('<br>'): url = url[:-4]
            self.add(name, url, auth)
            got.append(name)
        return got

    def watch(self, name):
        """ make feed ready for watching and mark it running. """
        logging.debug('trying %s hubbub feed' % name)
        item = self.byname(name)
        if item == None: raise NoSuchFeed(name)
        if not item.data.running:
            item.data.running = 1
            item.data.stoprunning = 0
            item.save()
            subscribe(item.data['url'])
        logging.info('hubbub - started %s watch' % name)

    def work(self, botname, type, channel, entries, url, *args, **kwargs):
        try:
            item = self.byurl(url)
            name = item.data.name
            try:
                fleet = getfleet()
                bot = fleet.byname(botname)
                if not bot and type:
                    bot = fleet.makebot(type, botname)
                if not bot:
                    bot = fleet.makebot('xmpp', botname)
            except NoSuchBotType, ex: logging.warn("hubbub - %s" % str(ex)) ; return
            if not bot: logging.error("hubbub - can't find %s bot in fleet" % type) ; return
            res2 = entries
            if not res2: logging.info("no updates for %s (%s) feed available" % (item.data.name, channel)) ; return
            if item.markup.get(jsonstring([name, channel]), 'reverse-order'): res2 = res2[::-1]
            if item.markup.get(jsonstring([name, channel]), 'all-lines'):
                for i in res2:
                    response = self.makeresponse(name, [i, ], channel)
                    try: bot.say(channel, response)
                    except Exception, ex: handle_exception()
            else:
                sep =  item.markup.get(jsonstring([name, channel]), 'separator')
                if sep: response = self.makeresponse(name, res2, channel, sep=sep)
                else: response = self.makeresponse(name, res2, channel)
                bot.say(channel, response)
        except Exception, ex: handle_exception()

    def incoming(self, data):
        """ process incoming hubbub data. """
        result = feedparser.parse(data)
        url = find_self_url(result.feed.links)
        logging.info("hubbub - in - %s - %s" % (url, data))
        try:
            item = self.byurl(url)
            if not item: logging.warn("hubbub - can't find feed for %s" % url) ; return
            if not item.data.running: logging.warn("hubbub - %s is not in running mode" % item.data.url) ; return
            if not item.data.url or item.data.url == 'urlnotset':
                item.data.url = url
                item.save()
            if item:
                loopover = item.data.watchchannels
                name = item.data.name
            else: logging.warn("hubbub - can't find %s item" % url) ; return
            logging.debug("loopover in %s peek is: %s" % (name, loopover))
            counter = 1
            for i in loopover:
                if len(i) == 3:
                    try: (botname, type, channel) = i
                    except:
                        try: (botname, type, channel) = loads(i)
                        except:
                            logging.info('hubbub - %s is not in the format (botname, bottype, channel)' % str(item))
                            continue
                else:
                    logging.debug('hubbub - %s is not in the format (botname, bottype, channel)' % item.data.url)
                    continue
                counter += 1
        except Exception, ex: handle_exception(txt=url)
        return True

    def getall(self):
        """ reconstruct all feeditems into self.feeds. """
        for name in self.data['names']: self.feeds[name] = HubbubItem(name)
        return self.feeds
       
    def ownercheck(self, name, userhost):
        """ check if userhost is the owner of feed. """
        try: return self.byname(name).ownercheck(userhost)
        except (KeyError, AttributeError): pass
        return False

    def makeresult(self, name, target, data):
        """ 
            make a result (txt) of a feed depending on its itemlist (tokens)
            and markup.

        """
        item = self.byname(name)
        res = []
        for j in data:
            tmp = {}
            if not item.itemslists.data[jsonstring([name, target])]: return []
            for i in item.itemslists.data[jsonstring([name, target])]:
                try: tmp[i] = unicode(j[i])
                except KeyError: continue
            res.append(tmp)
        return res


    def makeresponse(self, name, res, channel, sep=" .. "):
        """ loop over result to make a response. """
        item = self.byname(name)
        result = u"[%s] - " % name 
        try: itemslist = item.itemslists.data[jsonstring([name, channel])]
        except KeyError: 
            item = self.byname(name)
            if item == None: return "no %s rss item" % name
            else:
                item.itemslists.data[jsonstring([name, channel])] = ['title', 'link']
                item.itemslists.save()
        for j in res:
            if item.markup.get(jsonstring([name, channel]), 'skipmerge') and 'Merge branch' in j['title']: continue
            resultstr = u""
            for i in item.itemslists.data[jsonstring([name, channel])]:
                try:
                    ii = getattr(j, i)
                    if not ii: continue
                    ii = unicode(ii)
                    if ii.startswith('http://'):
                        if item.markup.get(jsonstring([name, channel]), 'tinyurl'):
                            try:
                                tinyurl = get_tinyurl(ii)
                                logging.debug('rss - tinyurl is: %s' % str(tinyurl))
                                if not tinyurl: resultstr += u"%s - " % ii
                                else: resultstr += u"%s - " % tinyurl[0]
                            except Exception, ex:
                                handle_exception()
                                resultstr += u"%s - " % item
                        else: resultstr += u"%s - " % ii
                    else: resultstr += u"%s - " % ii.strip()
                except (KeyError, AttributeError), ex:
                    logging.info('hubbub - %s - %s' % (name, str(ex)))
                    continue
            resultstr = resultstr[:-3]
            if resultstr: result += u"%s %s " % (resultstr, sep)
        return result[:-(len(sep)+2)]

    def stopwatch(self, name):
        """ disable running status of the feed. """
        try:
            feed = self.byname(name)
            feed.data.running = 0
            feed.save()
            return True
        except KeyError: pass
        return False

    def list(self):
        """ return feed names. """
        feeds = self.data['names']
        return feeds

    def runners(self):	
        """ show names/channels of running watchers. """
        result = []
        for name in self.data['names']:
            z = self.byname(name)
            if z.data.running == 1 and not z.data.stoprunning: result.append((z.data.name, z.data.watchchannels))
        return result

    def listfeeds(self, botname, type, channel):
        """ show names/channels of running watcher. """
        result = []
        for name in self.data['names']:
            z = self.byname(name)
            if not z or not z.data.running: continue
            if jsonstring([botname, type, channel]) in z.data.watchchannels or [botname, type, channel] in z.data.watchchannels:
                result.append(z.data.name)
        return result

    def getfeeds(self, channel, botname, type=None):
        """ get all feeds running in a channel. """
        chan = ChannelBase(channel, botname)
        return chan.data.feeds

    def url(self, name):
        """ return url of a feed. """
        feed = self.byname(name)
        if feed: return feed.data.url

    def seturl(self, name, url):
        """ set url of hubbub feed. """
        feed = self.byname(name)
        feed.data.url = url
        feed.save()
        return True

    def fetchdata(self, name):
        """ fetch the feed ourselves instead of receiving push items. """
        return self.byname(name).fetchdata()

    def scan(self, name):
        """ scan a rss url for tokens. """
        keys = []
        items = self.fetchdata(name)
        for item in items:
            for key in item:
                if key in allowedtokens: keys.append(key)            
        statdict = StatDict()
        for key in keys: statdict.upitem(key)
        return statdict.top()  

    def startwatchers(self):
        """ enable all runnable feeds """
        for name in self.data['names']:
            z = self.byname(name)
            if z.data.running: self.watch(z.data.name)

    def start(self, botname, type, name, channel):
        """ start a feed in a channel. """
        item = self.byname(name)
        if not item:
            logging.info("we don't have a %s feed" % name)
            return False
        target = channel
        if not jsonstring([botname, type, target]) in item.data.watchchannels and not [botname, type, target] in item.data.watchchannels:
            item.data.watchchannels.append([botname, type, target])
        item.itemslists.data[jsonstring([name, target])] = ['title', 'link']
        item.markup.set(jsonstring([name, target]), 'tinyurl', 1)
        item.data.running = 1
        item.data.stoprunning = 0
        item.save()
        watcher.watch(name)
        logging.debug("hubbub - started %s feed in %s channel" % (name, channel))
        return True

    def stop(self, botname, type, name, channel):
        """ stop watching a feed. """
        item = self.byname(name)
        if not item: return False
        try:
            logging.warn("trying to remove %s from %s feed list" % (name, channel))
            chan = ChannelBase(channel, botname)
            chan.data.feeds.remove(name)
            chan.save()
        except ValueError:
            logging.warn("can't remove %s from %s feed list" % (name, channel))
        try:
            item.data.watchchannels.remove([botname, type, channel])
            item.save()
            logging.debug("stopped %s feed in %s channel" % (name, channel))
        except ValueError: return False
        return True

    def clone(self, botname, type, newchannel, oldchannel):
        """ clone feeds over to a new wave. """
        feeds = self.getfeeds(oldchannel, botname)
        logging.debug("hubbub - clone - %s - %s - %s - %s - %s" % (botname, type, newchannel, oldchannel, feeds))
        for feed in feeds:
            self.stop(botname, type, feed, oldchannel)
            self.start(botname, type, feed, newchannel)
        return feeds

## work function

def work(botname, type, channel, result, item, *args, **kwargs):
     """ worker function used in defer. """
     watcher.work(botname, type, channel, result, item, *args, **kwargs)

## the watcher object

watcher = HubbubWatcher('hubbub')

## size function

def size():
    """ return number of watched rss entries. """
    return watcher.size()

## hb-subscribe command

def handle_hubbubsubscribe(bot, event):
    """ arguments: <feedname> [<url>] - subscribe to a hubbub feed, provide a url if the feed is not yet registered. """
    for name in event.args:
        item = watcher.byname(name)
        if not item: event.reply("%s feed is not yet added .. see hb-add" % name) ; continue
        url = item.data.url
        if not url: event.reply('please provide a url for %s feed' % name) ; return
        if not url.startswith('http://'): event.reply('%s doesnt start with "http://"' % url)
        if not watcher.data['urls'].has_key(name): watcher.add(name, url, event.channel)
        if not watcher.byname(name): watcher.add(name, url, event.channel)
        response = subscribe(url)
        event.reply("subscription send: %s - %s" % (url, response.status))

cmnds.add('hb-subscribe', handle_hubbubsubscribe, ['USER',])
examples.add('hb-subscribe', 'subscribe to a feed', 'hb-subscribe jsb-hg http://code.google.com/feeds/p/jsb/hgchanges/basi')

## hb-clone command

def handle_hubbubclone(bot, event):
    """ arguments: <channel> - clone the feeds running in a channel. """
    if not event.rest: event.missing('<channel>') ; return
    feeds = watcher.clone(bot.cfg.name, bot.type, event.channel, event.rest)
    event.reply('cloned the following feeds: ', feeds)
    bot.say(event.rest, "this wave is continued in %s" % event.url)
 
cmnds.add('hb-clone', handle_hubbubclone, 'USER')
examples.add('hb-clone', 'clone feeds into new channel', 'hb-clone #dunkbots')

## hb-cloneurl command

def handle_hubbubcloneurl(bot, event):
    """ arguments: <url> - clone urls from http://host/feeds. """
    if not event.rest: event.missing('<url>') ; return
    import urllib2
    try:
        feeds = watcher.cloneurl(event.rest, event.auth)
        event.reply('cloned the following feeds: ', feeds)
    except urllib2.HTTPError, ex: event.reply("hubbub - clone - %s" % str(ex))

cmnds.add('hb-cloneurl', handle_hubbubcloneurl, 'OPER')
examples.add('hb-cloneurl', 'clone feeds from remote url', 'hb-cloneurl http://jsonbot.org/feeds')

## hb-add command

def handle_hubbubadd(bot, ievent):
    """ arguments: <feedname> <url> - add a hubbub item (name/url combo). """
    try: (name, url) = ievent.args
    except ValueError: ievent.missing('<name> <url>') ; return
    result = subscribe(url)
    if int(result.status) > 200 and int(result.status) < 300:
       watcher.add(name, url, ievent.userhost)
       ievent.reply('%s feed added' % name)
    else: ievent.reply('%s feed NOT added. status code is %s' % (name, result.status))

cmnds.add('hb-add', handle_hubbubadd, 'USER')
examples.add('hb-add', 'hubbub-add <name> <url> to the watcher', 'hb-add jsb-hg http://code.google.com/feeds/p/jsb/hgchanges/basic')

## hb-watch command

def handle_hubbubwatch(bot, ievent):
    """ arguments: <feedname> - enable a feed for watching (per channel). """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    item = watcher.byname(name)
    if item == None: ievent.reply("we don't have a %s hubbub item" % name) ; return
    got = None
    if not item.data.running or item.data.stoprunning:
        item.data.running = 1
        item.data.stoprunning = 0
        got = True
        item.save()
        try: watcher.watch(name)
        except Exception, ex: ievent.reply(str(ex)) ; return
    if got: ievent.reply('watcher started')
    else: ievent.reply('already watching %s' % name)

cmnds.add('hb-watch', handle_hubbubwatch, 'USER')
examples.add('hb-watch', 'hubbub-watch <name> [seconds to sleep] .. go watching <name>', 'hb-watch gozerbot')

## hubbub-start command

def handle_hubbubstart(bot, ievent):
    """ arguments: <list of feeds> - start sending feeds to an user or channel. """
    feeds = ievent.args
    if not feeds: ievent.missing('<list of feeds>') ; return
    started = []
    cantstart = []
    if feeds[0] == 'all': feeds = watcher.list()
    for name in feeds:
        if watcher.start(bot.cfg.name, bot.type, name, ievent.channel):
            started.append(name)
            if name not in ievent.chan.data.feeds:
                ievent.chan.data.feeds.append(name)
                ievent.chan.save()
        else: cantstart.append(name)
    if bot.type == "wave":
        wave = ievent.chan
        if wave and wave.data:
            logging.debug("feed running in %s: %s" % (ievent.title, wave.data.feeds))
            if wave.data.loud:
                try: ievent.set_title("JSONBOT - %s - #%s" % (' - '.join(wave.data.feeds), str(wave.data.nrcloned)))
                except Exception, ex: handle_exception()
    if started: ievent.reply('started: ', started)
    else: ievent.reply("sorry can't start: ", cantstart)

cmnds.add('hb-start', handle_hubbubstart, ['USER', 'GUEST'])
examples.add('hb-start', 'hubbub-start <list of feeds> .. start a hubbub feed (per user/channel) ', 'hb-start gozerbot')

## hb-stop command

def handle_hubbubstop(bot, ievent):
    """ arguments: <list of feeds> - stop a hubbub feed to a user or channel. """
    if not ievent.args: ievent.missing('<list of feeds>') ; return
    feeds = ievent.args
    stopped = []
    cantstop = []
    if feeds[0] == 'all': feeds = watcher.listfeeds(bot.cfg.name, bot.type, ievent.channel)
    for name in feeds:
        if watcher.stop(bot.cfg.name, bot.type, name, ievent.channel):
            stopped.append(name)
            if name in ievent.chan.data.feeds:
                ievent.chan.data.feeds.remove(name)
                ievent.chan.save()
        else: cantstop.append(name)
    if stopped: ievent.reply('feeds stopped: ', feeds)
    elif cantstop: ievent.reply('failed to stop %s feed' % cantstop)
    ievent.done()

cmnds.add('hb-stop', handle_hubbubstop, ['USER', 'GUEST'])
examples.add('hb-stop', 'hubbub-stop <list of names> .. stop a hubbub feed (per user/channel) ', 'hb-stop gozerbot')

## hb-stopall command

def handle_hubbubstopall(bot, ievent):
    """ no arguments - stop all hubbub feeds to a channel. """
    if not ievent.rest: target = ievent.channel
    else: target = ievent.rest
    stopped = []
    feeds = watcher.getfeeds(target, bot.cfg.name)
    if feeds:
        for feed in feeds:
            if watcher.stop(bot.cfg.name, bot.type, feed, target):
                if feed in ievent.chan.data.feeds:
                    ievent.chan.data.feeds.remove(feed)
                    ievent.chan.save()
                stopped.append(feed)
        ievent.reply('stopped feeds: ', stopped)
    else: ievent.reply('no feeds running in %s' % target)

cmnds.add('hb-stopall', handle_hubbubstopall, ['HUBBUB', 'OPER'])
examples.add('hb-stopall', 'hubbub-stopall .. stop all hubbub feeds (per user/channel) ', 'hb-stopall')

## hb-channels command

def handle_hubbubchannels(bot, ievent):
    """ arguments: <feedname> - show channels of hubbub feed. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing("<feedname>") ; return
    item = watcher.byname(name)
    if item == None: ievent.reply("we don't have a %s hubbub object" % name) ; return
    if not item.data.watchchannels: ievent.reply('%s is not in watch mode' % name) ; return
    result = []
    for i in item.data.watchchannels: result.append(str(i))
    ievent.reply("channels of %s: " % name, result)

cmnds.add('hb-channels', handle_hubbubchannels, ['OPER', ])
examples.add('hb-channels', 'hb-channels <name> .. show channels', 'hb-channels gozerbot')

## hb-addchannel

def handle_hubbubaddchannel(bot, ievent):
    """ arguments: <feedname> [<botname>] [<bottype>] <channel> - add a channel to  hubbub feed. """
    try: (name, botname, type, channel) = ievent.args
    except ValueError:
        try:
            botname = bot.cfg.name
            (name, type, channel) = ievent.args
        except ValueError:
            try:
                botname = bot.cfg.name
                type = bot.type
                (name, channel) = ievent.args
                type = bot.type
            except ValueError:
                try:
                    botname = bot.cfg.name
                    name = ievent.args[0]
                    type = bot.type
                    channel = ievent.channel
                except IndexError: ievent.missing('<name> [<botname>][<bottype>] <channel>') ; return
    item = watcher.byname(name)
    if item == None: ievent.reply("we don't have a %s hubbub object" % name) ; return
    if not item.data.running: ievent.reply('%s watcher is not running' % name) ; return
    if jsonstring([botname, type, channel]) in item.data.watchchannels or [botname, type, channel] in item.data.watchchannels:
        ievent.reply('we are already monitoring %s on (%s,%s)' % (name, type, channel))
        return
    item.data.watchchannels.append([botname, type, channel])
    item.save()
    ievent.reply('%s added to %s hubbub item' % (channel, name))

cmnds.add('hb-addchannel', handle_hubbubaddchannel, ['OPER', ])
examples.add('hb-addchannel', 'add a channel to a feeds watchlist', '1) hb-addchannel gozerbot #dunkbots 2) hb-addchannel gozerbot main #dunkbots')

## hb-setitems command

def handle_hubbubsetitems(bot, ievent):
    """ arguments: <feedname> <list of tokens> - set items (tokens) of a feed, see hb-scan for a list of possible tokens. """
    try: (name, items) = ievent.args[0], ievent.args[1:]
    except ValueError: ievent.missing('<feedname> <tokens>') ; return
    target = ievent.channel
    feed =  watcher.byname(name)
    if not feed: ievent.reply("we don't have a %s feed" % name) ; return
    feed.itemslists.data[jsonstring([name, target])] = items
    feed.itemslists.save()
    ievent.reply('%s added to (%s,%s) itemslist' % (items, name, target))

cmnds.add('hb-setitems', handle_hubbubsetitems, ['GUEST', 'USER'])
examples.add('hb-setitems', 'set tokens of the itemslist (per user/channel)', 'hb-setitems gozerbot author author link pubDate')

## hb-additem command

def handle_hubbubadditem(bot, ievent):
    """ arguments: <feedname> <token> - add an item (token) to a feeds itemslist, this list is used to determine what to display. """
    try: (name, item) = ievent.args
    except ValueError: ievent.missing('<feedname> <token>') ; return
    target = ievent.channel
    feed = watcher.byname(name)
    if not feed: ievent.reply("we don't have a %s feed" % name) ; return
    try: feed.itemslists.data[jsonstring([name, target])].append(item)
    except KeyError: feed.itemslists.data[jsonstring([name, target])] = ['title', 'link']
    feed.itemslists.save()
    ievent.reply('%s added to (%s,%s) itemslist' % (item, name, target))

cmnds.add('hb-additem', handle_hubbubadditem, ['GUEST', 'USER'])
examples.add('hb-additem', 'add a token to the itemslist (per user/channel)', 'hb-additem gozerbot link')

## hb-delitem command

def handle_hubbubdelitem(bot, ievent):
    """ arguments: <feedname> <token> - delete item (token) from a feeds itemlist. """
    try: (name, item) = ievent.args
    except ValueError: ievent.missing('<name> <item>') ; return
    target = ievent.channel
    feed = watcher.byname(name)
    if not feed: ievent.reply("we don't have a %s feed" % name) ; return
    try:
        feed.itemslists.data[jsonstring([name, target])].remove(item)
        feed.itemslists.save()
    except (NoSuchFeed, ValueError): ievent.reply("we don't have a %s feed" % name) ; return
    ievent.reply('%s removed from (%s,%s) itemslist' % (item, name, target))

cmnds.add('hb-delitem', handle_hubbubdelitem, ['GUEST', 'USER'])
examples.add('hb-delitem', 'remove a token from the itemslist (per user/channel)', 'hb-delitem gozerbot link')

## hb-markuplist command

def handle_hubbubmarkuplist(bot, ievent):
    """ no arguments - show possible markups that can be used. """
    ievent.reply('possible markups ==> ' , possiblemarkup)

cmnds.add('hb-markuplist', handle_hubbubmarkuplist, ['USER', 'GUEST'])
examples.add('hb-markuplist', 'show possible markup entries', 'hb-markuplist')

## hb-markup command

def handle_hubbubmarkup(bot, ievent):
    """ arguments: <feedname> - show the markup of a feed (channel specific). """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    target = ievent.channel
    feed = watcher.byname(name)
    if not feed: ievent.reply("we don't have a %s feed" % name) ; return
    try: ievent.reply(str(feed.markup[jsonstring([name, target])]))
    except KeyError: pass

cmnds.add('hb-markup', handle_hubbubmarkup, ['GUEST', 'USER'])
examples.add('hb-markup', 'show markup list for a feed (per user/channel)', 'hb-markup gozerbot')

## hb-addmarkup command

def handle_hubbubaddmarkup(bot, ievent):
    """ arguments: <feedname> <item> <value> - add a markup to a feeds markuplist, this list determines how we display things. """
    try: (name, item, value) = ievent.args
    except ValueError: ievent.missing('<feedname> <item> <value>') ; return
    target = ievent.channel
    try: value = int(value)
    except ValueError: pass
    feed = watcher.byname(name)
    if not feed: ievent.reply("we don't have a %s feed" % name) ; return
    try:
        feed.markup.set(jsonstring([name, target]), item, value)
        feed.markup.save()
        ievent.reply('%s added to (%s,%s) markuplist' % (item, name, target))
    except KeyError: ievent.reply("no (%s,%s) feed available" % (name, target))

cmnds.add('hb-addmarkup', handle_hubbubaddmarkup, ['GUEST', 'USER'])
examples.add('hb-addmarkup', 'add a markup option to the markuplist (per user/channel)', 'hb-addmarkup gozerbot all-lines 1')

## hb-delmarkup command

def handle_hubbubdelmarkup(bot, ievent):
    """ arguments: <feedname> <item> - delete markup item from a feed's markuplist. """
    try: (name, item) = ievent.args
    except ValueError: ievent.missing('<feedname> <item>') ; return
    target = ievent.channel
    feed = watcher.byname(name)
    if not feed: ievent.reply("we don't have a %s feed" % name) ; return
    try: del feed.markup[jsonstring([name, target])][item]
    except (KeyError, TypeError): ievent.reply("can't remove %s from %s feed's markup" %  (item, name)) ; return
    feed.markup.save()
    ievent.reply('%s removed from (%s,%s) markuplist' % (item, name, target))

cmnds.add('hb-delmarkup', handle_hubbubdelmarkup, ['GUEST', 'USER'])
examples.add('hb-delmarkup', 'remove a markup option from the markuplist (per user/channel)', 'hb-delmarkup gozerbot all-lines')

## hb-delchannel command

def handle_hubbubdelchannel(bot, ievent):
    """ arguments: <feedname> [<botname>] [<bottype>] [<channel>] - delete channel from hubbub feed. """
    bottype = None
    try: (name, botname, bottype, channel) = ievent.args
    except ValueError:
        try:
            botname = bot.cfg.name
            (name, type, channel) = ievent.args
        except ValueError:
            try:
                botname = bot.cfg.name
                name = ievent.args[0]
                type = bot.type
                channel = ievent.channel
            except IndexError:
                ievent.missing('<feedname> [<botname>] [<bottype>] [<channel>]')
                return
    item = watcher.byname(name)
    if item == None: ievent.reply("we don't have a %s object" % name) ; return
    if jsonstring([botname, type, channel]) in item.data.watchchannels:
        item.data.watchchannels.remove(jsonstring([botname, type, channel]))
        ievent.reply('%s removed from %s hubbub item' % (channel, name))
    elif [type, channel] in item.data.watchchannels:
        item.data.watchchannels.remove([botname, type, channel])
        ievent.reply('%s removed from %s hubbub item' % (channel, name))
    else:
        ievent.reply('we are not monitoring %s on (%s,%s)' % (name, type, channel))
        return
    item.save()

cmnds.add('hb-delchannel', handle_hubbubdelchannel, ['OPER', ])
examples.add('hubbub-delchannel', 'remove a channel from a feeds watchlist', '1) hb-delchannel gozerbot #dunkbots 2) hb-delchannel gozerbot main #dunkbots')

## hb-stopwatch command

def handle_hubbubstopwatch(bot, ievent):
    """ arguments: <feedname> - stop watching a feed. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    item = watcher.byname(name)
    if not item: ievent.reply("there is no %s item" % name) ; return
    if not watcher.stopwatch(name): ievent.reply("can't stop %s watcher" % name) ; return
    ievent.reply('stopped %s hubbub watch' % name)

cmnds.add('hb-stopwatch', handle_hubbubstopwatch, ['OPER', ])
examples.add('hb-stopwatch', 'hubbub-stopwatch <name> .. stop polling <name>', 'hb-stopwatch gozerbot')

## hb-get command

def handle_hubbubget(bot, ievent):
    """ arguments: <feedname> - fetch feed data. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    channel = ievent.channel
    item = watcher.byname(name)
    if item == None: ievent.reply("we don't have a %s item" % name) ; return
    try: result = watcher.fetchdata(name)
    except Exception, ex: ievent.reply('%s error: %s' % (name, str(ex))) ; return
    if item.markup.get(jsonstring([name, channel]), 'reverse-order'): result = result[::-1]
    response = watcher.makeresponse(name, result, ievent.channel)
    if response: ievent.reply("results of %s: %s" % (name, response))
    else: ievent.reply("can't make a reponse out of %s" % name)

cmnds.add('hb-get', handle_hubbubget, ['HUBBUB', 'USER'], threaded=True)
examples.add('hb-get', 'hubbub-get <name> .. get data from <name>', 'hb-get gozerbot')

## hb-running command

def handle_hubbubrunning(bot, ievent):
    """ no arguments - show which feeds are running. """
    result = watcher.runners()
    resultlist = []
    teller = 1
    for i in result: resultlist.append("%s %s" % (i[0], i[1]))
    if resultlist: ievent.reply("running hubbub watchers: ", resultlist, nr=1)
    else: ievent.reply('nothing running yet')

cmnds.add('hb-running', handle_hubbubrunning, ['HUBBUB', 'USER'])
examples.add('hb-running', 'hubbub-running .. get running feeds', 'hb-running')

## hb-list command

def handle_hubbublist(bot, ievent):
    """ no arguments - return list of available feeds. """
    result = watcher.list()
    result.sort()
    if result: ievent.reply("hubbub items: ", result)
    else: ievent.reply('no hubbub items yet')

cmnds.add('hb-list', handle_hubbublist, ['GUEST', 'USER'])
examples.add('hb-list', 'get list of hubbub items', 'hb-list')

## hb-url command

def handle_hubbuburl(bot, ievent):
    """ arguments: <feedname> - return url of feed. """
    try:
        name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    if not watcher.ownercheck(name, ievent.userhost):
        ievent.reply("you are not the owner of the %s feed" % name)
        return
    result = watcher.url(name)
    if not result: ievent.reply("can't fetch url for %s" % name) ; return
    try:
        if ':' in result.split('/')[1]:
            if not ievent.msg: ievent.reply('run this command in a private message') ; return
    except (TypeError, ValueError, IndexError): pass
    ievent.reply('url of %s: %s' % (name, result))

cmnds.add('hb-url', handle_hubbuburl, ['OPER', ])
examples.add('hb-url', 'hb-url <name> .. get url from hubbub item', 'hb-url gozerbot')

## hb-itemslist command

def handle_hubbubitemslist(bot, ievent):
    """ arguments: <feedname> - show itemslist (tokens) of hubbub item. """
    try:name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    feed = watcher.byname(name)
    if not feed: ievent.reply("we don't have a %s feed" % name) ; return
    try: itemslist = feed.itemslists.data[jsonstring([name, ievent.channel])]
    except KeyError: ievent.reply("no itemslist set for (%s, %s)" % (name, ievent.channel)) ; return
    ievent.reply("itemslist of (%s, %s): " % (name, ievent.channel), itemslist)

cmnds.add('hb-itemslist', handle_hubbubitemslist, ['GUEST', 'USER'])
examples.add('hb-itemslist', 'hb-itemslist <name> .. get itemslist of <name> ', 'hb-itemslist gozerbot')

## hb-scan command

def handle_hubbubscan(bot, ievent):
    """ arguments: <feedname>  - scan feed for available tokens. """
    try: name = ievent.args[0]
    except IndexError: ievent.missing('<feedname>') ; return
    if not watcher.byname(name): ievent.reply('no %s feeds available' % name) ; return
    try: result = watcher.scan(name)
    except Exception, ex: ievent.reply(str(ex)) ; return
    if result == None: ievent.reply("can't get data for %s" % name) ; return
    res = []
    for i in result: res.append("%s=%s" % i)
    ievent.reply("tokens of %s: " % name, res)

cmnds.add('hb-scan', handle_hubbubscan, ['USER', 'GUEST'])
examples.add('hb-scan', 'hb-scan <name> .. get possible items of <name> ', 'hb-scan gozerbot')

## hb-feeds command

def handle_hubbubfeeds(bot, ievent):
    """ arguments: [<channel>] - show what feeds are running in a channel. """
    try: channel = ievent.args[0]
    except IndexError: channel = ievent.channel
    try:
        result = watcher.getfeeds(channel, bot.cfg.name)
        if result: ievent.reply("feeds running: ", result)
        else: ievent.reply('no feeds running')
    except Exception, ex: ievent.reply("ERROR: %s" % str(ex))

cmnds.add('hb-feeds', handle_hubbubfeeds, ['USER', 'GUEST'])
examples.add('hb-feeds', 'hb-feeds <name> .. show what feeds are running in a channel', '1) hb-feeds 2) hb-feeds #dunkbots')

def handle_hubbubregister(bot, ievent):
    """ arguments: <feedname> <url> - register a url and start the feed in one pass. """
    target = ievent.waveid or ievent.channel
    if len(ievent.args) > 2: ievent.reply("feed name needs to be 1 word.") ; return
    try: (name, url) = ievent.args
    except ValueError:
        try: name = ievent.args[0]
        except IndexError: ievent.reply("i need a feed name and a feed url to work with") ; return
        item = watcher.byname(name)
        if item:
            if not name in watcher.getfeeds(ievent.channel, bot.cfg.name):
                watcher.start(bot.cfg.name, bot.type, name, target)
                if name not in ievent.chan.data.feeds:
                    ievent.chan.data.feeds.append(name)
                    ievent.chan.save()
                ievent.reply('started %s feed. entries will show up when the feed is updated.' % name)
            else: ievent.reply("feed %s is already running." % name)
        else: ievent.reply("i don't know a %s feed. please enter name and url." % name)
        return
    if not url.startswith("http"): ievent.reply("the feedurl needs to start with http(s)://") ; return
    result = subscribe(url)
    if int(result.status) > 200 and int(result.status) < 300:
        if watcher.add(name, url, ievent.userhost):
            watcher.start(bot.cfg.name, bot.type, name, target)
            ievent.reply('started %s feed. entries will show up when the feed is updated.' % name)
            return
        else:
            ievent.reply("there already exists a %s feed. please choose a different name" % name)
            return
    else:
        ievent.reply('feed %s NOT added. Status code is %s. please check if the feed is valid.' % (name, result.status))

cmnds.add('hb-register', handle_hubbubregister, ['USER', 'GUEST'])
examples.add('hb-register', 'hb-register .. register url and start it in one pass', 'hb-register hgrepo http://code.google.com/feeds/p/jsb/hgchanges/basic')
