# jsb/plugs/common/wikipedia.py
#
#

""" query wikipedia .. use countrycode to select a country specific wikipedia. """

## jsb imports

from jsb.utils.url import geturl, striphtml
from jsb.utils.generic import splittxt, handle_exception, fromenc
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.utils.rsslist import rsslist

## generic imports

from urllib import quote
import re
import logging

## defines

wikire = re.compile('start content(.*?)end content', re.M)

## searchwiki function

def searchwiki(txt, lang='en'):
    """ parse wiki data. """
    input = []     
    for i in txt.split():
        if i.startswith('-'):
            if len(i) != 3: continue
            else: lang = i[1:]
            continue
        input.append(i.strip().capitalize())
    what = "_".join(input)
    url = u'http://%s.wikipedia.org/wiki/Special:Export/%s' % (lang, quote(what.encode('utf-8')))
    url2 = u'http://%s.wikipedia.org/wiki/%s' % (lang, quote(what.encode('utf-8')))
    txt = getwikidata(url)
    if not txt: return ("", url2)
    if 'from other capitalisation' in txt:
        what = what.title()
        url = u'http://%s.wikipedia.org/wiki/Special:Export/%s' % (lang, quote(what.encode('utf-8')))
        url2 = u'http://%s.wikipedia.org/wiki/%s' % (lang, quote(what.encode('utf-8')))
        txt = getwikidata(url)
    if '#REDIRECT' in txt or '#redirect' in txt:
        redir = ' '.join(txt.split()[1:])
        url = u'http://%s.wikipedia.org/wiki/Special:Export/%s' % (lang, quote(redir.encode('utf-8')))
        url2 = u'http://%s.wikipedia.org/wiki/%s' % (lang, quote(redir.encode('utf-8')))
        txt = getwikidata(url)
    return (txt, url2)

## getwikidata function

def getwikidata(url):
    """ fetch wiki data """
    result = geturl(url)
    if not result: return
    res = rsslist(result)
    txt = ""
    for i in res:
        try:
            logging.debug(unicode(i))
            txt = i['text']
            break
        except: pass
    txt = re.sub('\[\[(.*?)\]\]', '<b>\g<1></b>', txt)
    txt = re.sub('{{(.*?)}}', '<i>\g<1></i>', txt)
    txt = re.sub('==(.*?)==', '<h3>\g<1></h3>', txt)
    txt = re.sub('=(.*?)=', '<h2>\g<1></h2>', txt)
    txt = re.sub('\*(.*?)\n', '<li>\g<1></li>', txt)
    txt = re.sub('\n\n', '<br><br>', txt)
    txt = re.sub('\s+', ' ', txt)
    txt = txt.replace('|', ' - ')
    return txt

## wikipedia command

resultre1 = re.compile("(<li>.*?</li>)")
resultre2 = re.compile("(<h2>.*?</h2>)")

def handle_wikipedia(bot, ievent):
    """ arguments: <searchtxt> ["-"<countrycode>] -  search wikipedia, you can provide an optional country code.  """
    if not ievent.rest: ievent.missing('<searchtxt>') ; return
    showall = False
    res = searchwiki(ievent.rest)
    if not res[0]: ievent.reply('no result found') ; return
    prefix = u'%s ===> ' % res[1]
    result = resultre1.findall(res[0])
    if result:
        if bot.type == "sxmpp" and not ievent.groupchat: showall = True
        ievent.reply(prefix, result, dot="<br>", showall=showall)
        return
    result2 = resultre2.findall(res[0])
    if result2:
        if bot.type == "sxmpp" and not ievent.groupchat: showall = True
        ievent.reply(prefix, result2, dot="<br>", showall=showall)
        return
    else: ievent.reply("no data found on %s" % event.rest)

cmnds.add('wikipedia', handle_wikipedia, ['USER', 'GUEST'])
examples.add('wikipedia', 'search wikipedia for <what>','1) wikipedia bot 2) wikipedia -nl bot')
