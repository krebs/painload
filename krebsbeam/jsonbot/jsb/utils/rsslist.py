# jsb/utils/rsslist.py
#
#

""" create a list of rss data """

## jsb imports

from exception import handle_exception

## basic imports

import xml.dom.minidom

## gettext function

def gettext(nodelist):
    """ get text data from nodelist """
    result = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE or node.nodeType == node.CDATA_SECTION_NODE:
            stripped = node.data.strip()
            if stripped: result += stripped
    return result

def makersslist(xlist, nodes , d={}):
    """ recurse until txt is found """
    for i in nodes:
        if i.nodeType == i.ELEMENT_NODE:
            dd = d[i.nodeName] = {}
            makersslist(xlist, i.childNodes, dd)
            if dd: xlist.append(dd)
        txt = gettext(i.childNodes)
        if txt: d[i.nodeName] = txt
        
def rsslist(txt):
    """ create list of dictionaries with rss data """
    dom = xml.dom.minidom.parseString(txt)
    result = []
    makersslist(result, dom.childNodes)
    return result
