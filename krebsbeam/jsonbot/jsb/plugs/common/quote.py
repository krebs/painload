# jsb/plugs/common/quote.py
#
#

""" manage quotes. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.persist import PlugPersist

## basic imports

import random

## defines

quotes = PlugPersist('quotes.data')

if not quotes.data.index:
    quotes.data.index = 0

## quote-add command

def handle_quoteadd(bot, event):
    """ arguments: <quote> - add a quote. """
    if not event.rest: event.missing("<quote>") ; return
    quotes.data.index += 1
    quotes.data[quotes.data.index] = event.rest
    quotes.save()
    event.reply("quote %s added" % quotes.data.index)

cmnds.add('quote-add', handle_quoteadd, ['USER', 'GUEST'])
examples.add('quote-add' , 'add a quote to the bot', 'quote-add blablabla')

## quote command

def handle_quote(bot, event):
    """ no arguments - get a quote. """
    possible = quotes.data.keys()
    possible.remove('index')
    if possible: nr = random.choice(possible) ; event.reply("#%s %s" % (nr, quotes.data[nr]))
    else: event.reply("no quotes yet.")

cmnds.add('quote', handle_quote, ['USER', 'GUEST'])
examples.add('quote' , 'get a quote from the bot', 'quote')
