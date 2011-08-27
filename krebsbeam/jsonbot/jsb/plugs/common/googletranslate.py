# jsb/plugs/common/googletranslate.py
#
#
# author: melmoth

""" use google translate. """

## jsb imports

from jsb.lib.examples import examples
from jsb.lib.commands import cmnds
from jsb.utils.url import geturl2
from jsb.imports import getjson

## basic imports

import re
from urllib import quote, unquote

## defines

URL = r"http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&q=%(text)s&langpair=%(from)s|%(to)s"

def parse_pair(text):
    trans = re.match("^(?P<from>[a-z]{2}) +(?P<to>[a-z]{2}) +(?P<txt>.*)$", text)
    if not trans: return {}
    return {'from': trans.group('from'),
            'to':   trans.group('to'),
            'text': quote(trans.group('txt'))}

## translate command

def handle_translate(bot, event):
    """ arguments: <countrycode to translate from> <countrycode to translate to> <txt> - translate the given txt with google translate. """
    if not event.rest:  event.missing("<from> <to> <text>") ; return
    query = parse_pair(event.rest.strip())
    if not query:  event.missing("<from> <to> <text>") ; return
    rawresult = {}
    try: rawresult = getjson().loads(geturl2(URL % query))
    except: event.reply("query to google failed") ; return
    # rawresult = {"responseData": {"translatedText":"test"}, "responseDetails": None, "responseStatus": 201}
    if rawresult['responseStatus'] != 200: event.reply("error in the query: ", rawresult) ; return
    if 'responseData' in rawresult:
        if 'translatedText' in rawresult['responseData']:
            translation = rawresult['responseData']['translatedText']
            event.reply(unquote(translation))
        else: event.reply("no text available")
    else: event.reply("something is wrong, probably the API changed")

cmnds.add("translate", handle_translate, ["OPER", "USER", "GUEST"])
examples.add("translate", "use google translate to translate txt.", "translate nl en top bot")
