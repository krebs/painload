# jsb/plugs/core/uniq.py
#
#

""" used in a pipeline .. unique elements. """

__author__ = "Wijnand 'tehmaze' Modderman - http://tehmaze.com"
__license__ = 'BSD'

## jsb imports

from jsb.lib.examples import examples
from jsb.lib.commands import cmnds
from jsb.utils.generic import waitforqueue

## uniq command

def handle_uniq(bot, ievent):
    """ no arguments - uniq the result list, use this command in a pipeline. """
    if not ievent.inqueue:
        ievent.reply('use uniq in a pipeline')
        return
    result = waitforqueue(ievent.inqueue, 3000)
    if not result:
        ievent.reply('no data')
        return
    result = list(result)
    if not result: ievent.reply('no result')
    else: ievent.reply("result: ", result)

cmnds.add('uniq', handle_uniq, ['OPER', 'USER', 'GUEST'])
examples.add('uniq', 'sort out multiple elements', 'list ! uniq')
