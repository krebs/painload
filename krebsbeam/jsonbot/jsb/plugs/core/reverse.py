# jsb/plugs/core/reverse.py
#
# 

""" reverse pipeline or reverse <txt>. """

__copyright__ = 'this file is in the public domain'
__author__ = 'Hans van Kranenburg <hans@knorrie.org>'

## jsb imports

from jsb.utils.generic import waitforqueue
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples

## basic imports

import types

## reverse command

def handle_reverse(bot, ievent):
    """ arguments: [<string>] - reverse string or use in a pipeline. """
    if ievent.rest: result = ievent.rest
    else: result = waitforqueue(ievent.inqueue, 5000)
    if not result: ievent.reply("reverse what?") ; return
    if type(result) == types.ListType: ievent.reply("results: ", result[::-1])
    else: ievent.reply(result[::-1])

cmnds.add('reverse', handle_reverse, ['OPER', 'USER', 'GUEST'])
examples.add('reverse', 'reverse text or pipeline', '1) reverse gozerbot 2) list ! reverse')
