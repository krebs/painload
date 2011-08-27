# jsb/plugs/common/colors.py
#
#

""" use the morph to add color to selected words. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.lib.callbacks import first_callbacks
from jsb.lib.morphs import outputmorphs
from jsb.lib.persiststate import PlugState
from jsb.utils.lazydict import LazyDict

## basic imports

import re
import logging

## defines

state = PlugState()
state.define("colormapping", {})

## the morph

def docolormorph(txt, event):
    """ add the color to the txt. """
    if not txt: return txt
    if event and not event.bottype == "irc": return txt
    splitted = txt.split()
    for s in splitted:
        for t, color in state.data.colormapping.iteritems():
            try: c = int(color)
            except: logging.warn("color - %s is not a digit" % color) ; continue
            if c < 0: d = "00"
            elif c < 9: d = "0%s" % c
            elif c > 15: d = "15"
            else: d = "%s" % c           
            if t in s: txt = txt.replace(s, "\003%s%s\003" % (d, s))
    return txt

## color-list command

def handle_colorlist(bot, event):
    """ no arguments - show list of color mappings. """
    event.reply("colors set: ", state.data.colormapping)

cmnds.add("color-list", handle_colorlist, ["OPER"])
examples.add("color-list", "show color mapping", "color-list")

## color-add command

def handle_coloradd(bot, event):
    """ arguments: <txt> <color> - add a txt/color mapping .. color must be a number between 0 and 9. """
    try: (txt, color) = event.rest.rsplit(" ", 1)
    except (TypeError, ValueError): event.missing("<txt> <color>") ; return
    try: c = int(color)
    except (ValueError, TypeError): event.reply("color must be between 0 and 9") ; return 
    if c < 0: c = 0
    if c > 15: c = 15
    state.data.colormapping[txt] = c
    state.save()
    event.reply("color of %s set to %s" % (txt, c))

cmnds.add("color-add", handle_coloradd, ["OPER"])
examples.add("color-add", "add a text color replacement to the morphs", "color-add dunker 8")

## color-del command

def handle_colordel(bot, event):
    """ arguments: <txt> - remove color mapping. """
    if not event.rest: event.missing("<txt>") ; return
    try: del state.data.colormapping[event.rest] ; state.save()
    except KeyError: event.reply("we are not morphing %s" % event.rest)
    event.reply("color removed for %s" % event.rest)

cmnds.add("color-del", handle_colordel, ["OPER"])
examples.add("color-del", "remove a text color replacement from the morphs", "color-del dunker")

## start

def init():
    """ init the colors plugin, add the colormorph. """
    outputmorphs.add(docolormorph)

def bogus(bot, event):
    """ bogus startup function to load the color morph on startup. """
    pass

first_callbacks.add("START", bogus)
