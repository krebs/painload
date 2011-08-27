# plugs/todo.py
#
#

""" gozerbot compat todo. """

## jsb imports

from jsb.compat.persist import Persist

## basic imports

import time

## Todoitem class

class Todoitem:

    """ a todo item """

    def __init__(self, name, descr, ttime=None, duration=None, warnsec=None, priority=None, num=0):
        self.name = name
        self.time = ttime
        self.duration = duration
        self.warnsec = warnsec
        self.descr = descr
        self.priority = priority
        self.num = num

    def __str__(self):
        return "name: %s num: %d time: %s duration: %s warnsec: %s \
description: %s priority: %s" % (self.name, self.num, \
time.ctime(self.time), self.duration, self.warnsec, self.descr, self.priority)

## Todolist class

class Todolist:

    """ a dict faking list of todo items .. index is number """

    def __init__(self):
        self.max = 0
        self.data = {}

    def __len__(self):
        return len(self.data)

    def __getitem__(self, num):
        return self.data[num]

    def __delitem__(self, num):
        del self.data[num]

    def __iter__(self):
        tmplist = self.data.values()
        tmplist.sort(lambda x, y: cmp(x.priority, y.priority), reverse=True)
        return tmplist.__iter__()

    def append(self, item):
        """ add todo item """
        self.max += 1
        item.num = self.max
        self.data[self.max] = item

    def __str__(self):
        return str(self.data)

## Todo class

class Todo(Persist):

    """ Todoos """

    def __init__(self, filename):
        Persist.__init__(self, filename)
        if not self.data:
            return
        for key in self.data.keys():
            todoos = self.data[key]
            for (k, v) in todoos.data.items():
                v.num = k
            newd = Todolist()
            for i in todoos:
                newd.append(i)
            self.data[key] = newd

    def size(self):
        """ return number of todo entries """
        return len(self.data)

    def get(self, name):
        """ get todoos of <name> """
        if self.data.has_key(name):
            return self.data[name]

    def add(self, name, txt, ttime, warnsec=0):
        """ add a todo """
        name = name.lower()
        if not self.data.has_key(name):
            self.data[name] = Todolist()
        self.data[name].append(Todoitem(name, txt.strip(), ttime, warnsec=0-warnsec))
        self.save()
        return len(self.data[name])

    def addnosave(self, name, txt, ttime):
        """ add but don't save """
        name = name.lower()
        if not self.data.has_key(name):
            self.data[name] = Todolist()
        self.data[name].append(Todoitem(name, txt, ttime))

    def reset(self, name):
        name = name.lower()
        if self.data.has_key(name):
           self.data[name] = Todolist()
        self.save()

    def delete(self, name, nr):
        """ delete todo item """
        if not self.data.has_key(name):
            return 0
        todoos = self.data[name]
        try:
            if todoos[nr].warnsec:
                alarmnr = 0 - todoos[nr].warnsec
                if alarmnr > 0:
                    alarms.delete(alarmnr)
            del todoos[nr]
        except KeyError:
            return 0
        self.save()
        return 1

    def toolate(self, name):
        """ show if there are any time related todoos that are too late """
        now = time.time()
        teller = 0
        for i in self.data[name]:
            if i.time < now:
                teller += 1
        return teller

    def timetodo(self, name):
        """ show todoos with time field set """
        result = []
        if not self.data.has_key(name):
            return result
        for i in self.data[name]:
            if i.time:
                result.append(i)
        return result

    def withintime(self, name, time1, time2):
        """ show todoos within time frame """
        result = []
        if not self.data.has_key(name):
            return result
        for i in self.data[name]:
            if i.time >= time1 and i.time < time2:
                result.append(i)
        return result

    def setprio(self, who, itemnr, prio):
        """ set priority of todo item """
        try:
            todoitems = self.get(who)
            todoitems[itemnr].priority = prio
            self.save()
            return 1
        except (KeyError, TypeError):
            pass

    def settime(self, who, itemnr, ttime):
        """ set time of todo item """
        try:
            todoitems = self.get(who)
            todoitems[itemnr].time = ttime
            self.save()
            return 1
        except (KeyError, TypeError):
            pass

