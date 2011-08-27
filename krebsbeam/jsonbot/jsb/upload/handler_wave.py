# handler_wave.py
#
#

""" this handler handles all the wave jsonrpc requests. """

## jsb imports

from jsb.version import getversion
from jsb.lib.errors import NoSuchCommand
from jsb.lib.boot import boot

## gaelib imports

from jsb.drivers.gae.wave.bot import WaveBot

## basic imports

import logging
import os

## defines

logging.info(getversion('GAE WAVE'))
boot()

# the bot

bot = WaveBot(domain="googlewave.com")

def main():
    bot.run()

if __name__ == "__main__":
    main()
