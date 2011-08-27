# jsb/plugs/gae/gae.py
#
#

""" Google Application Engine related commands. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples

## gae-flushcache command

def handle_gaeflushcache(bot, ievent):
    """ flush the cache .. flush all with no arguments otherwise delete specific. """
    from google.appengine.api.memcache import flush_all, delete
    if not ievent.rest: flush_all()
    else: delete(ievent.rest)
    ievent.done()

cmnds.add('gae-flushcache', handle_gaeflushcache, 'OPER')
examples.add('gae-flushcache', 'flush the bots cache', 'gae-flushcache')

## gae-stats command

def handle_gaeadminstats(bot, ievent):
    """ show bot stats. """
    from google.appengine.api.memcache import get_stats
    ievent.reply("cache: %s" % str(get_stats()))

cmnds.add('gae-stats', handle_gaeadminstats, 'OPER')
examples.add('gae-stats', 'show bots stats', 'gae-stats')
