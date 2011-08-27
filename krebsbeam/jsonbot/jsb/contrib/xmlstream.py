##   xmlstream.py
##
##   Copyright (C) 2001 Matthew Allum
##
##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU Lesser General Public License as published
##   by the Free Software Foundation; either version 2, or (at your option)
##   any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU Lesser General Public License for more details.


"""\
xmlstream.py provides simple functionality for implementing
XML stream based network protocols. It is used as a  base
for jabber.py.

xmlstream.py manages the network connectivity and xml parsing
of the stream. When a complete 'protocol element' ( meaning a
complete child of the xmlstreams root ) is parsed the dipatch
method is called with a 'Node' instance of this structure.
The Node class is a very simple XML DOM like class for
manipulating XML documents or 'protocol elements' in this
case.

"""

# $Id: xmlstream.py,v 1.45 2004/02/03 16:33:37 snakeru Exp $

import time
import sys
import re
import socket
import logging
from base64 import encodestring
import xml.parsers.expat
import cgi
from xml.sax.saxutils import unescape, escape

__version__ = VERSION = "0.5"

ENCODING = 'utf-8'      # Though it is uncommon, this is the only right setting.
ustr = str

BLOCK_SIZE  = 1024     ## Number of bytes to get at at time via socket
                       ## transactions

def XMLescape(txt):
    "Escape XML entities"
    #logging.debug("XMLescape - incoming - %s" % txt)
    if not txt:
        return txt
    txt = txt.replace("&", "&amp;")
    txt = txt.replace("<", "&lt;")
    txt = txt.replace(">", "&gt;")
    #txt = txt.replace('"', "'")
    return txt

def XMLunescape(txt):
    "Unescape XML entities"
    if not txt:
        return txt
    txt = txt.replace("&gt;", ">")
    txt = txt.replace("&lt;", "<")
    txt = txt.replace("&amp;", "&")
    txt = txt.replace("&apos;", "'")
    return txt

class error(object):
    def __init__(self, value):
        self.value = str(value)
    def __str__(self):
        return self.value

class Node(object):
    """A simple XML DOM like class"""
    def __init__(self, tag=None, parent=None, attrs={}, payload=[], node=None):
        if node:
            if type(node)<>type(self): node=NodeBuilder(node).getDom()
            self.name,self.namespace,self.attrs,self.data,self.kids,self.parent = \
                node.name,node.namespace,node.attrs,node.data,node.kids,node.parent
        else:
            self.name,self.namespace,self.attrs,self.data,self.kids,self.parent = 'tag','',{},[],[],None

        if tag: self.namespace, self.name = (['']+tag.split())[-2:]

        if parent: self.parent = parent

#        if self.parent and not self.namespace: self.namespace=self.parent.namespace   # Doesn't checked if this neccessary

        for attr in attrs.keys():
            self.attrs[attr]=attrs[attr]

        for i in payload:
            if type(i)==type(self): self.insertNode(i)
            else: self.insertXML(i)
#            self.insertNode(Node(node=i))     # Alternative way. Needs perfomance testing.

    def setParent(self, node):
        "Set the nodes parent node."
        self.parent = node

    def getParent(self):
        "return the nodes parent node."
        return self.parent

    def getName(self):
        "Set the nodes tag name."
        return self.name

    def setName(self,val):
        "Set the nodes tag name."
        self.name = val

    def putAttr(self, key, val):
        "Add a name/value attribute to the node."
        self.attrs[key] = val

    def getAttr(self, key):
        "Get a value for the nodes named attribute."
        try: return self.attrs[key]
        except: return None

    def getAttributes(self):
        "Get a value for the nodes named attribute."
        return self.attrs

    def putData(self, data):
        "Set the nodes textual data"
        self.data.append(data)

    def insertData(self, data):
        "Set the nodes textual data"
        self.data.append(data)

    def getData(self):
        "Return the nodes textual data"
        return ''.join(self.data)

    def getDataAsParts(self):
        "Return the node data as an array"
        return self.data

    def getNamespace(self):
        "Returns the nodes namespace."
        return self.namespace

    def setNamespace(self, namespace):
        "Set the nodes namespace."
        self.namespace = namespace

    def insertTag(self, name=None, attrs={}, payload=[], node=None):
        """ Add a child tag of name 'name' to the node.

            Returns the newly created node.
        """
        newnode = Node(tag=name, parent=self, attrs=attrs, payload=payload, node=node)
        self.kids.append(newnode)
        return newnode

    def insertNode(self, node):
        "Add a child node to the node"
        self.kids.append(node)
        return node

    def insertXML(self, xml_str):
        "Add raw xml as a child of the node"
        newnode = NodeBuilder(xml_str).getDom()
        self.kids.append(newnode)
        return newnode

    def __str__(self):
        return self._xmlnode2str()

    def _xmlnode2str(self, parent=None):
        """Returns an xml ( string ) representation of the node
         and it children"""
        s = "<" + self.name
        if self.namespace:
            if parent and parent.namespace != self.namespace:
                s = s + " xmlns = '%s' " % self.namespace
        for key in self.attrs.keys():
            val = ustr(self.attrs[key])
            s = s + " %s='%s'" % ( key, XMLescape(val) )
        s = s + ">"
        cnt = 0
        if self.kids != None:
            for a in self.kids:
                if (len(self.data)-1) >= cnt: s = s + XMLescape(self.data[cnt])
                s = s + a._xmlnode2str(parent=self)
                cnt=cnt+1
        if (len(self.data)-1) >= cnt: s = s + XMLescape(self.data[cnt])
        if not self.kids and s[-1:]=='>':
            s=s[:-1]+' />'
        else:
            s = s + "</" + self.name + ">"
        return s

    def getTag(self, name, index=None):
        """Returns a child node with tag name. Returns None
        if not found."""
        for node in self.kids:
            if node.getName() == name:
                if not index: return node
                if index is not None: index-=1
        return None

    def getTags(self, name):
        """Like getTag but returns a list with matching child nodes"""
        nodes=[]
        for node in self.kids:
            if node.getName() == name:
               nodes.append(node)
        return nodes

    def getChildren(self):
        """Returns a nodes children"""
        return self.kids

    def removeTag(self,tag):
        """Pops out specified child and returns it."""
        if type(tag)==type(self):
            try:
                self.kids.remove(tag)
                return tag
            except: return None
        for node in self.kids:
            if node.getName()==tag:
                self.kids.remove(node)
                return node

class NodeBuilder(object):
    """builds a 'minidom' from data parsed to it. Primarily for insertXML
       method of Node"""
    def __init__(self,data=None):
        self._parser = xml.parsers.expat.ParserCreate()
        self._parser.StartElementHandler  = self.unknown_starttag
        self._parser.EndElementHandler    = self.unknown_endtag
        self._parser.CharacterDataHandler = self.handle_data
        self.__depth = 0
        self._dispatch_depth = 1
        self.last_is_data = False
        self._ptr = Node()
        if data: self._parser.Parse(data,1)

    def unknown_starttag(self, tag, attrs):
        """XML Parser callback"""
        self.__depth = self.__depth + 1
        if self.__depth == self._dispatch_depth:
            self._mini_dom = Node(tag=tag, attrs=attrs)
            self._ptr = self._mini_dom
        elif self.__depth > self._dispatch_depth:
            self._ptr.kids.append(Node(tag=tag,parent=self._ptr,attrs=attrs))
            self._ptr = self._ptr.kids[-1]
        else:                           ## it the stream tag:
            if attrs.has_key('id'):
                self._incomingID = attrs['id']
        self.last_is_data = False

    def unknown_endtag(self, tag ):
        """XML Parser callback"""
        if self.__depth == self._dispatch_depth:
            self.dispatch(self._mini_dom)
        elif self.__depth > self._dispatch_depth:
            self._ptr = self._ptr.parent
        self.__depth = self.__depth - 1
        self.last_is_data = False

    def handle_data(self, data):
        """XML Parser callback"""
        if self.last_is_data:
            self._ptr.data[-1] += data
        else:
            self._ptr.data.append(data)
            self.last_is_data = True

    def dispatch(self,dom):
        pass

    def getDom(self):
        return self._mini_dom
