# jsb/utils/textutils.py
#
#

## basic imports

import cgi
import re
import htmlentitydefs

## unescape_charref function

def unescape_charref(ref): 
    """ ask maze. """
    name = ref[2:-1] 
    base = 10 
    if name.startswith("x"): 
        name = name[1:] 
        base = 16 
    return unichr(int(name, base)) 

## replace_entities function

def replace_entities(match):
    """ ask maze. """ 
    ent = match.group() 
    if ent[1] == "#":  return unescape_charref(ent) 
    repl = htmlentitydefs.najsbcodepoint.get(ent[1:-1]) 
    if repl is not None: repl = unichr(repl) 
    else: repl = ent 
    return repl 

## html_unescape function

def html_unescape(data): 
    ''' unescape (numeric) HTML entities. '''
    return re.sub(r"&#?[A-Za-z0-9]+?;", replace_entities, data) 

## html_escape function

def html_escape(data):
    ''' escape HTML entities. '''
    return cgi.escape(data)
