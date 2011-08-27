# jsb/plugs/common/todo.py
#
#

"""
    manage todo lists per users .. a time/data string can be provided to set 
    time on a todo item.

"""

## jsb imports

from jsb.utils.generic import getwho
from jsb.utils.timeutils import strtotime, striptime, today
from jsb.utils.locking import lockdec
from jsb.utils.exception import handle_exception
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.users import users
from jsb.lib.persist import PlugPersist
from jsb.lib.persiststate import UserState
from jsb.utils.lazydict import LazyDict

## basic imports

import time
import thread
import os
from datetime import datetime, timedelta
from time import localtime

## defines

todolock = thread.allocate_lock()
locked = lockdec(todolock)

## Todo-class

class Todo(LazyDict):
    pass

## TodoList class

class TodoList(UserState):

    def __init__(self, name, *args, **kwargs):
        UserState.__init__(self, name, "todo", *args, **kwargs)
        if self.data.list: self.data.list = [LazyDict(x) for x in self.data.list]
        else: self.data.list = []
        self.name = name

    def add(self, txt, ttime=0, duration=0, warnsec=0, priority=0):
        """ add a todo """
        todo = Todo()
        todo.time = ttime
        todo.duration = duration
        todo.warnsec = warnsec
        todo.priority = priority
        todo.txt = txt.strip()
        self.data.list.append(todo)
        self.save()
        return len(self.data.list)

    def delete(self, indexnr):
        """ delete a todo. """
        del self.data.list[indexnr-1]
        self.save()
        return self

    def clear(self):
        """ clear the todo list. """
        self.data.list = []
        self.save()
        return self

    def toolate(self):
        """ check what todo items are too late. """
        res = []
        now = time.time()
        for todo in self.data.list:
            if todo.time < now: res.append(todo)
        return res

    def withintime(self, before, after):
        """ show todo items within a time frame. """
        res = []
        for todo in self.data.list:
            if todo.time > before and todo.time < after: res.append(todo)
        return res

    def timetodo(self):
        """ return todo items that have a time set. """
        min = 0        
        res = []
        for todo in self.data.list:
            if todo.time > min: res.append(todo)
        return res

## todo command

def handle_todo(bot, ievent):
    """ arguments: [<item>] - show todo's or set todo item, a time/date can be given. """
    if len(ievent.args) > 0: handle_todo2(bot, ievent) ; return
    if ievent.options and ievent.options.dochan: name = ievent.channel
    else: name = ievent.user.data.name
    try: todoos = TodoList(name).data.list
    except KeyError: ievent.reply('i dont have todo info for %s' % user.name) ; return
    saytodo(bot, ievent, todoos, name)

def handle_todo2(bot, ievent):
    """ set todo item """
    if not ievent.rest: ievent.missing("<what>") ; return
    else: what = ievent.rest
    if ievent.options and ievent.options.dochan: name = ievent.channel
    else: name = ievent.user.data.name
    if not name: ievent.reply("can't find username for %s" % ievent.auth) ; return
    ttime = strtotime(what)
    nr = 0
    todo = TodoList(name)
    if not ttime == None: ievent.reply('time detected ' + time.ctime(ttime)) ; nr = todo.add(what, ttime)
    else: nr = todo.add(what)
    ievent.reply('todo item %s added' % nr)

cmnds.add('todo', handle_todo, ['USER', 'GUEST'])
examples.add('todo', 'show todo items or add a todo item, a time can be given as well.', '1) todo 2) todo program the bot 3) todo 22:00 sleep')

## todo-done command

def handle_tododone(bot, ievent):
    """ arguments: <list of nrs> - remove todo items """
    if len(ievent.args) == 0: ievent.missing('<list of nrs>') ; return
    try:
        nrs = []
        for i in ievent.args: nrs.append(int(i))
        nrs.sort()
    except ValueError: ievent.reply('%s is not an integer' % i) ; return
    if ievent.options and ievent.options.dochan: name = ievent.channel
    else: name = ievent.user.data.name
    nrdone = 0
    failed = []
    todo = TodoList(name)
    for i in nrs[::-1]:
        try: del todo.data.list[i-1] ; nrdone += 1
        except IndexError: continue
        except Exception, ex: failed.append(str(i)) ; handle_exception()
    if failed: ievent.reply('failed to delete %s' % ' .. '.join(failed))
    if nrdone == 1: todo.save() ; ievent.reply('%s item deleted' % nrdone)
    elif nrdone == 0: ievent.reply('no items deleted')
    else:todo.save() ; ievent.reply('%s items deleted' % nrdone)

cmnds.add('todo-done', handle_tododone, ['USER', 'GUEST'])
examples.add('todo-done', 'todo-done <listofnrs> .. remove items from todo list', '1) todo-done 1 2) todo-done 3 5 8')

## todo-time command

def handle_todotime(bot, ievent):
    """ no arguments: todo-time - show time related todoos """
    if ievent.options and ievent.options.dochan: name = ievent.channel
    else: name = ievent.user.data.name
    todo = TodoList(name)
    todoos = todo.timetodo()
    saytodo(bot, ievent, todoos, name)

cmnds.add('todo-time', handle_todotime, ['USER', 'GUEST'])
examples.add('todo-time', 'todo-time .. show todo items with time fields', 'todo-time')

## todo-week command

def handle_todoweek(bot, ievent):
    """ no arguments - show time related todo items for this week """
    name = ievent.user.data.name or ievent.channel
    todo = TodoList(name)
    todoos = todo.withintime(today(), today()+7*24*60*60)
    saytodo(bot, ievent, todoos, name)

cmnds.add('todo-week', handle_todoweek, ['USER', 'GUEST'])
examples.add('todo-week', 'todo-week .. todo items for this week', 'todo-week')

## todo-today command

def handle_today(bot, ievent):
    """ no arguments - show time related todo items for today """
    if ievent.options and ievent.options.dochan: name = ievent.channel
    else: name = ievent.user.data.name
    todo = Todolist(name)
    now = time.time()
    todoos = todo.withintime(now, now+3600*24)
    saytodo(bot, ievent, todoos, name)

cmnds.add('todo-today', handle_today, ['USER', 'GUEST'])
examples.add('todo-today', 'todo-today .. todo items for today', 'todo-today')

## todo-tomorrow command

def handle_tomorrow(bot, ievent):
    """ no arguments - show time related todo items for tomorrow """
    if ievent.options and ievent.options.dochan: name = ievent.channel
    else: name = ievent.user.data.name
    todo = TodoList(name)
    if ievent.rest:
        what = ievent.rest
        ttime = strtotime(what)
        if ttime != None:
            if ttime < today() or ttime > today() + 24*60*60:
                ievent.reply("%s is not tomorrow" % time.ctime(ttime + 24*60*60))
                return
            ttime += 24*60*60
            ievent.reply('time detected ' + time.ctime(ttime))
            what = striptime(what)
        else: ttime = today() + 42*60*60
        todo.add(what, ttime)   
        ievent.reply('todo added')    
        return
    todoos = todo.withintime(today()+24*60*60, today()+2*24*60*60)
    saytodo(bot, ievent, todoos, name)

cmnds.add('todo-tomorrow', handle_tomorrow, ['USER', 'GUEST'])
examples.add('todo-tomorrow', 'todo-tomorrow .. todo items for tomorrow', 'todo-tomorrow')

## todo-setprio command

def handle_setpriority(bot, ievent):
    """ arguments: <itemnr> <prio> - show priority on todo item. """
    try: (itemnr, prio) = ievent.args
    except ValueError: ievent.missing('<itemnr> <priority>') ; return
    try: itemnr = int(itemnr) ; prio = int(prio)
    except ValueError: ievent.missing('priority needs to be an integer') ; return
    if ievent.options and ievent.options.dochan: name = ievent.channel
    else: name = ievent.user.data.name
    todo = TodoList(name)
    try:
        todo.data.list[itemnr-1].priority = prio
        todo.save()
        ievent.reply('priority set')
    except IndexError: ievent.reply("no %s item in todolist" % str(itemnr))

cmnds.add('todo-setprio', handle_setpriority, ['USER', 'GUEST'])
examples.add('todo-setprio', 'set todo priority', 'todo-setprio 2 5')

## todo-settime command

def handle_todosettime(bot, ievent):
    """ arguments: <itemnr> <timestring> - set time on todo item """
    ttime = strtotime(ievent.rest)
    if ttime == None: ievent.reply("can't detect time") ; return   
    txt = striptime(ievent.rest)
    try: (itemnr, ) = txt.split()[0] 
    except (ValueError, TypeError): ievent.missing('<itemnr> <timestring>') ; return
    try: itemnr = int(itemnr)
    except ValueError: ievent.missing('item number needs to be a string.') ; return
    if ievent.options and ievent.options.dochan: name = ievent.channel
    else: name = ievent.user.data.name
    todo = TodoList(name)
    try:
        todo.data.list[itemnr-1].time = ttime
        todo.save()
        ievent.reply('time of todo %s set to %s' % (itemnr, time.ctime(ttime)))
    except IndexError: ievent.reply("%s item in todolist" % str(itemnr))

cmnds.add('todo-settime', handle_todosettime, ['USER', 'GUEST'])
examples.add('todo-settime', 'set todo time', '1) todo-settime owner 3 2-2-2010 2) todo-settime 2 22:00')

## todo-getprio command

def handle_getpriority(bot, ievent):
    """ arguments: <itemnr> - get priority of todo item. """
    try: (who, itemnr) = ievent.args
    except ValueError:
        try: itemnr = ievent.args[0]
        except IndexError: ievent.missing('[<channel|name>] <itemnr>') ; return
    if not who: ievent.reply("can't find username for %s" % ievent.auth) ; return
    try: itemnr = int(itemnr)
    except ValueError: ievent.missing('[<channel|name>] <itemnr>') ; return
    if ievent.options and ievent.options.dochan: name = ievent.channel
    else: name = ievent.user.data.name
    todo = TodoList(name)
    try: prio = todo.data.list[itemnr].priority ; ievent.reply('priority is %s' % prio)
    except IndexError: ievent.reply("%s item in todolist" % str(itemnr))

cmnds.add('todo-getprio', handle_getpriority, ['USER', 'GUEST'])
examples.add('todo-getprio', 'todo-getprio [<channel|name>] <itemnr> .. get todo priority', '1) todo-getprio #dunkbots 5 2) todo-getprio 3')

## saytodo function

def saytodo(bot, ievent, todoos, target=""):
    """ output todo items. """
    if not todoos: ievent.reply('nothing todo for %s ;]' % target or "you") ; return
    result = []
    now = time.time()
    counter = 1
    todoos.sort(lambda a, b: cmp(b.priority,a.priority))
    for i in todoos:
        res = ""
        res += "%s) " % counter
        counter += 1
        if i.priority: res += "[%s] " % i.priority
        if i.time and not i.time == 0:
            if i.time < now: res += 'TOO LATE: '
            res += "%s %s " % (time.ctime(float(i.time)), i.txt)
        else: res += "%s " % i.txt
        result.append(res.strip())
    if result: ievent.reply("todo for %s: " % target or "you", result, dot=" ")
