# jsb/gozerevent.py
#
#

""" 
    basic event used in jsb. supports json dumping and loading plus toxml
    functionality. 
"""

## jsb imports

from jsb.utils.url import striphtml
from jsb.lib.eventbase import EventBase

## dom imports

from jsb.contrib.xmlstream import NodeBuilder, XMLescape, XMLunescape

## for exceptions

import xml.parsers.expat

## xmpp imports

from jsb.drivers.xmpp.namespace import attributes, subelements

## basic imports

import logging

## GozerEvent class

class GozerEvent(EventBase):

    """ dictionairy to store xml stanza attributes. """

    def __init__(self, input={}):
        if input == None: EventBase.__init__(self)
        else: EventBase.__init__(self, input)
        try: self['fromm'] = self['from']
        except (KeyError, TypeError): self['fromm'] = ''

    def __getattr__(self, name):
        """ override getattribute so nodes in payload can be accessed. """
        if not self.has_key(name) and self.has_key('subelements'):
            for i in self['subelements']:
                if name in i: return i[name]
        return EventBase.__getattr__(self, name, default="")

    def get(self, name):
        """ get a attribute by name. """
        if self.has_key('subelements'): 
            for i in self['subelements']:
                if name in i: return i[name]
        if self.has_key(name): return self[name] 
        return EventBase()

    def tojabber(self):
        """ convert the dictionary to xml. """
        res = dict(self)
        if not res:
            raise Exception("%s .. toxml() can't convert empty dict" % self.name)
        elem = self['element']
        main = "<%s" % self['element']
        for attribute in attributes[elem]:
            if attribute in res:
                if res[attribute]: main += u" %s='%s'" % (attribute, XMLescape(res[attribute]))
                continue
        main += ">"
        gotsub = False
        if res.has_key('html'):
            if res['html']:
                main += u'<html xmlns="http://jabber.org/protocol/xhtml-im"><body xmlns="http://www.w3.org/1999/xhtml">%s</body></html>' % res['html']
                gotsub = True
        if res.has_key('txt'):
            if res['txt']:
                main += u"<body>%s</body>" % XMLescape(res['txt'])
                gotsub = True
        for subelement in subelements[elem]:
            if subelement == "body": continue
            try:
                data = res[subelement]
                if data:
                    main += "<%s>%s</%s>" % (subelement, XMLescape(data), subelement)
                    gotsub = True
            except KeyError: pass
        if gotsub: main += "</%s>" % elem
        else:
            main = main[:-1]
            main += "/>"
        return main

    def str(self):
        """ convert to string. """
        result = ""
        elem = self['element']
        for item, value in dict(self).iteritems():
            if item in attributes[elem] or item in subelements[elem] or item == 'txt': result += "%s='%s' " % (item, value)
        return result
