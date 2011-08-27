# jsb/plugs/common/8b.py
#
#

""" run the eight ball. """

## jsb imports

from jsb.utils.exception import handle_exception
from jsb.lib.commands import cmnds
from jsb.lib.examples import examples

## basic imports

import re
import random

## defines

balltxt=[
    "Signs point to yes.",
    "Yes.",
    "Most likely.",
    "Without a doubt.",
    "Yes - definitely.",
    "As I see it, yes.",
    "You may rely on it.",
    "Outlook good.",
    "It is certain.",
    "It is decidedly so.",
    "Reply hazy, try again.",
    "Better not tell you now.",
    "Ask again later.",
    "Concentrate and ask again.",
    "Cannot predict now.",
    "My sources say no.",
    "Very doubtful.",
    "My reply is no.",
    "Outlook not so good.",
    "Don't count on it."
    ]

## 8b command

def handle_8b(bot, ievent):
    """ no arguments - throw the eight ball. """
    ievent.reply(random.choice(balltxt))

cmnds.add('8b', handle_8b, ['OPER', 'USER', 'GUEST'])
examples.add('8b', 'show what the magic 8 ball has to say.', '8b')
