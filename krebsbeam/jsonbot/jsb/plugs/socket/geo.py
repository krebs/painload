# jsb/plugs/socket/geo.py
#
#

""" This product includes GeoLite data created by MaxMind, available from http://maxmind.com/ """


## jsb imports

from jsb.lib.callbacks import callbacks
from jsb.lib.examples import examples
from jsb.lib.commands import cmnds
from jsb.utils.url import geturl2
from jsb.utils.exception import handle_exception
from jsb.imports import getjson

## basic imports

from socket import gethostbyname
import re

## defines

URL = "http://geoip.pidgets.com/?ip=%s&format=json"

## querygeoipserver function

def querygeoipserver(ip):
    ipinfo = getjson().loads(geturl2(URL % ip))
    return ipinfo

## host2ip function

def host2ip(query):
    ippattern =   re.match(r"^([0-9]{1,3}\.){3}[0-9]{1,3}$", query)
    hostpattern = re.match(r"(\w+://)?(?P<hostname>\S+\.\w+)", query)
    ip = ""
    if ippattern: ip = ippattern.group(0)
    elif hostpattern:
        try: ip = gethostbyname(hostpattern.group('hostname'))
        except: pass
    return ip

## geo command

def handle_geo(bot, event):
    """ arguments: <ipnr> - do a geo lookup. """
    if not event.rest: 
        event.missing("<ipnr>")
        return
    query = event.rest.strip()
    ip = host2ip(query)
    if not ip: event.reply("Couldn't look up the hostname") ; return
    event.reply("geo of %s is: " % ip, querygeoipserver(ip))

cmnds.add("geo", handle_geo, ["OPER", "GEO"])
examples.add("geo", "do a geo lookup on ip nr", "geo 127.0.0.1")

## callbacks

def handle_geoPRE(bot, event):
    if "." in event.hostname and event.chan and event.chan.data.dogeo: return True 

def handle_geoJOIN(bot, event):
    event.reply("geo - doing query on %s" % event.hostname)
    try:
        result = querygeoipserver(host2ip(event.hostname))
        if result: event.reply("%s lives in %s, %s (%s)" % (event.nick, result['city'], result['country_name'], result['country_code']))
        else: event.reply("no result")
    except: handle_exception()

callbacks.add("JOIN", handle_geoJOIN, handle_geoPRE)

## geo-on command

def handle_geoon(bot, event):
    """ no arguments - enable geo lookup on JOIN. """
    event.chan.data.dogeo = True
    event.chan.save()
    event.done()

cmnds.add("geo-on", handle_geoon, ["OPER"])
examples.add("geo-on", "enable geo loopups.", "geo-on")

## geo-off command

def handle_geooff(bot, event):
    """ no arguments - disable geo lookup on JOIN. """
    event.chan.data.dogeo = False
    event.chan.save()
    event.done()

cmnds.add("geo-off", handle_geooff, ["OPER"])
examples.add("geo-off", "disable geo loopups.", "geo-off")
