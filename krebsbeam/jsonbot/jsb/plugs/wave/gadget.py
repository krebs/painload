# jsb/plugs/wave/gadget.py
#
#

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.persist import PlugPersist

## defines

gadgeturls = PlugPersist('gadgeturls')

gadgeturls.data['gadget'] = 'https://jsonbot.appspot.com/gadget.xml'
gadgeturls.data['poll'] = 'https://jsonbot.appspot.com/poll.xml'
gadgeturls.data['iframe'] = 'https://jsonbot.appspot.com/iframe.xml'
gadgeturls.data['loadiframe'] = 'https://jsonbot.appspot.com/loadiframe.xml'

## load functions

def loadroot(event, url):
    if event.rootblip:
        from waveapi import element
        event.rootblip.append(element.Gadget(url))
        return True
    else: event.reply("can't find root blip.") ; return False

def load(event, url):
    if event.blip:
        from waveapi import element
        event.blip.append(element.Gadget(url))
        return True
    else: event.reply("can't find root blip.") ; return False

## gadget-load command

def handle_gadgetload(bot, event):
    if event.bottype != "wave": event.reply("this command only works in google wave.") ; return
    if not event.rest: event.missing('<gadgetname>') ; return
    try:
        url = gadgeturls.data[event.rest]
        if load(event, url): event.reply('loaded %s' % url)
    except KeyError: event.reply("we don't have a url for %s" % event.rest)

cmnds.add("gadget-load", handle_gadgetload, 'USER')
examples.add("gadget-load", "load a gadget into a blip", "gadget-load")

## gadget-loadroot command

def handle_gadgetloadroot(bot, event):
    if event.bottype != "wave": event.reply("this command only works in google wave.") ; return
    if not event.rest: event.missing('<gadgetname>') ; return
    try:
        url = gadgeturls.data[event.rest]
        if loadroot(event, url): event.reply('loaded %s' % url)
    except KeyError: event.reply("we don't have a url for %s" % event.rest)

cmnds.add("gadget-loadroot", handle_gadgetloadroot, 'USER')
examples.add("gadget-loadroot", "load a gadget into the root blip", "gadget-loadroot")

## gadget-iframe command

def handle_gadgetiframe(bot, event):
    if event.bottype != "wave": event.reply("this command only works in google wave.") ; return
    if not event.rest: event.missing('<url>') ; return
    try:
        url = gadgeturls.data['loadiframe'] + "?&iframeurl=%s" % event.rest
        event.reply('loading %s' % url)
        load(event, url)
    except KeyError: event.reply("we don't have a iframe url")

cmnds.add("gadget-iframe", handle_gadgetiframe, 'USER')
examples.add("gadget-iframe", "load a url into a iframe", "gadget-iframe")

## gadget-addurl command

def handle_gadgetaddurl(bot, event):
    try: (name, url) = event.args
    except ValueError: event.missing('<name> <url>') ; return
    if not gadgeturls.data.has_key(name):
        gadgeturls.data[name] = url
        gadgeturls.save()
    else: event.reply("we already have a %s gadget" % name)

cmnds.add("gadget-addurl", handle_gadgetaddurl, 'USER')
examples.add("gadget-addurl", "store a gadget url", "gadget-addurl jsb https://jsonbot.appspot.com/iframe.xml")

## gadget-delurl command

def handle_gadgetdelurl(bot, event):
    try: (name, url) = event.args
    except ValueError: event.missing('<name> <url>') ; return
    gadgeturls.data[name] = url
    gadgeturls.save()

cmnds.add("gadget-delurl", handle_gadgetdelurl, 'OPER')
examples.add("gadget-delurl", "delete a gadget url", "gadget-delurl mygadget")

## gadget-list command

def handle_gadgetlist(bot, event):
    result = []
    for name, url in gadgeturls.data.iteritems(): result.append("%s - %s" % (name, url))
    event.reply("available gadgets: ", result)

cmnds.add("gadget-list", handle_gadgetlist, 'USER')
examples.add("gadget-list", "list known gadget urls", "gadget-list")

## gadget-console command

def handle_gadgetconsole(bot, event):
    if event.bottype != "wave": event.reply("this command only works in google wave.") ; return
    wave = event.chan
    if wave.data.feeds and wave.data.dotitle:
        event.set_title("JSONBOT - %s #%s" % (" - ".join(wave.data.feeds), str(wave.data.nrcloned)))
    from waveapi import element
    event.append("loading ...\n")
    event.append(element.Gadget('http://jsonbot.appspot.com/console.xml?gadget_cache=0'))

cmnds.add("gadget-console", handle_gadgetconsole, 'OPER')
examples.add("gadget-console", "load the console gadget", "gadget-console")
