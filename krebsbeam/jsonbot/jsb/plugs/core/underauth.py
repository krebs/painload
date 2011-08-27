# jsb/plugs/core/underauth.py
#
#

""" handle non-ident connection on undernet. """

## copyright

__copyright__ = 'this file is in the public domain'
__author__ = 'aafshar@gmail.com'

## jsb imports

from jsb.lib.callbacks import callbacks

##  pre_underauth_cb precondition

def pre_underauth_cb(bot, ievent):
    """ 
        Only respond to the message like:
        NOTICE AUTH :*** Your ident is disabled or broken, to continue
        to connect you must type /QUOTE PASS 16188.

    """
    args = ievent.arguments
    try: return (args[0] == 'AUTH' and args[-3] == '/QUOTE' and args[-2] == 'PASS')
    except Exception, ex: return False

## underauth_cb callback

def underauth_cb(bot, ievent):
    """ Send the raw command to the server. """
    bot._raw(' '.join(ievent.arguments[-2:]))

callbacks.add('NOTICE', underauth_cb, pre_underauth_cb)
