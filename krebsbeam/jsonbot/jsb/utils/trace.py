# jsb/utils/trace.py
#
#

""" trace related functions """

## basic imports

import sys
import os

## defines

stopmarkers = ['waveapi', 'jsb', 'myplugs', 'python2.5', 'python2.6']

## calledfrom function

def calledfrom(frame):
    """ return the plugin name where given frame occured. """
    try:
        filename = frame.f_back.f_code.co_filename
        plugfile = filename.split(os.sep)
        if plugfile:
            mod = []
            for i in plugfile[::-1]:
                mod.append(i)
                if i in stopmarkers: break
            modstr = '.'.join(mod[::-1])[:-3]
            if 'handler_' in modstr: modstr = modstr.split('.')[-1]
    except AttributeError: modstr = None
    del frame
    return modstr

## callstack function

def callstack(frame):
    """ return callstack trace as a string. """
    result = []
    loopframe = frame
    while 1:
        try:
            filename = loopframe.f_back.f_code.co_filename
            plugfile = filename.split(os.sep)
            if plugfile:
                mod = []
                for i in plugfile[::-1]:
                    mod.append(i)
                    if i in stopmarkers: break
                modstr = '.'.join(mod[::-1])[:-3]
                if 'handler_' in modstr: modstr = modstr.split('.')[-1]
            result.append("%s:%s" % (modstr, loopframe.f_back.f_lineno))
            loopframe = loopframe.f_back
        except: break
    del frame
    return result

## whichmodule function

def whichmodule(depth=1):
    """ return filename:lineno of the module. """
    try:
        frame = sys._getframe(depth)
        plugfile = frame.f_back.f_code.co_filename[:-3].split('/')
        lineno = frame.f_back.f_lineno
        mod = []
        for i in plugfile[::-1]:
            mod.append(i)
            if i in stopmarkers: break
        modstr = '.'.join(mod[::-1]) + ':' + str(lineno)
        if 'handler_' in modstr: modstr = modstr.split('.')[-1]
    except AttributeError: modstr = None
    del frame
    return modstr

## whichplugin function

def whichplugin(depth=1):
    """ return filename:lineno of the module. """
    try:
        frame = sys._getframe(depth)
        plugfile = frame.f_back.f_code.co_filename[:-3].split('/')
        lineno = frame.f_back.f_lineno
        mod = []
        for i in plugfile[::-1]: 
            mod.append(i)
            if i in stopmarkers: break
        modstr = '.'.join(mod[::-1])
        if 'handler_' in modstr: modstr = modstr.split('.')[-1]
    except AttributeError: modstr = None
    del frame
    return modstr
