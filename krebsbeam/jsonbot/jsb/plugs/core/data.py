# jsb/plugs/core/data.py
#
#

""" data dumper commands. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples

## data-event command

def handle_dataevent(bot, event):
    """ no arguments - dump event to json. """
    event.reply(event.tojson())

cmnds.add("data-event", handle_dataevent, "OPER")
examples.add('data-event', 'dump event data', 'data-event')

## data-chan command

def handle_datachan(bot, event):
    """ no arguments - dump channel data to json. """
    event.reply(event.chan.data.tojson())

cmnds.add("data-chan", handle_datachan, "OPER")
examples.add('data-chan', 'dump channel data', 'data-chan')

## data-bot command

def handle_databot(bot, event):
    """ no arguments - dump bot as json dict. """
    event.reply(bot.tojson())

cmnds.add("data-bot", handle_databot, "OPER")
examples.add('data-bot', 'dump bot data', 'data-bot')
