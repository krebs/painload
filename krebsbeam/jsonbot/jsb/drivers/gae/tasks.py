# jsb/gae/tasks.py
#
#

""" appengine tasks related classes and functions. """

## jsb imports

from jsb.utils.exception import handle_exception

## google imports

from google.appengine.api.labs.taskqueue import Task, Queue

## simplejson imports

from jsb.imports import getjson
json = getjson()

## basic imports

import uuid

## Event Classes

class BotEvent(Task):
    pass

## defines

queues = []
for i in range(9):
    queues.append(Queue("queue" + str(i)))

## start_botevent function

def start_botevent(bot, event, speed=5):
    """ start a new botevent task. """
    try:
        try: speed = int(speed)
        except: speed = 5
        event.botevent = True
        if event.usercmnd[0] == "!": e = event.usercmnd[1:]
        else: e = event.usercmnd
        name = e + "-" + str(uuid.uuid4())
        payload = json.dumps({ 'bot': bot.tojson(),
                          'event': event.tojson()
                        })
        be = BotEvent(name=name, payload=payload, url="/tasks/botevent")
        try: queues[int(speed)].add(be)
        except TypeError: queues[speed].add(be)
    except Exception, ex: 
        handle_exception()
