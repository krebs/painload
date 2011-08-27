# jsb/plugs/core/botevent.py
#
#

""" provide handling of host/tasks/botevent tasks. """

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.lib.tasks import taskmanager
from jsb.lib.botbase import BotBase
from jsb.lib.eventbase import EventBase
from jsb.utils.lazydict import LazyDict
from jsb.lib.factory import BotFactory
from jsb.lib.callbacks import first_callbacks, callbacks, last_callbacks

## simplejson imports

from jsb.imports import getjson
json = getjson()

## basic imports

import logging

## boteventcb callback

def boteventcb(inputdict, request, response):
    logging.warn(inputdict)
    logging.warn(dir(request))
    logging.warn(dir(response))
    body = request.body
    logging.warn(body)
    payload = json.loads(body)
    try:
        botjson = payload['bot']
        logging.warn(botjson)
        cfg = LazyDict(json.loads(botjson))
        logging.warn(str(cfg))
        bot = BotFactory().create(cfg.type, cfg)
        logging.warn("botevent - created bot: %s" % bot.dump())
        eventjson = payload['event']
        logging.warn(eventjson)
        event = EventBase()
        event.update(LazyDict(json.loads(eventjson)))
        logging.warn("botevent - created event: %s" % event.dump())
        event.isremote = True
        event.notask = True
        bot.doevent(event)
    except Exception, ex: handle_exception()

taskmanager.add('botevent', boteventcb)

