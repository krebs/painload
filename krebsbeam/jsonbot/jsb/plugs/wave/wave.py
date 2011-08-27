# jsb/plugs/wave/wave.py
#
#

""" wave related commands. """

## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.examples import examples
from jsb.utils.exception import handle_exception
from jsb.lib.persist import PlugPersist
from jsb.lib.callbacks import callbacks
from jsb.lib.plugins import plugs
from jsb.drivers.gae.wave.waves import Wave

## basic imports

import logging

## wave-start command

def handle_wavestart(bot, event):
    """ start a protected wave. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return

    wave = event.chan
    event.reply("cloning ...")
    newwave = wave.clone(bot, event, participants=["jsb@appspot.com", event.userhost])

    if not newwave:
        event.reply("can't create new wave")
        return

    newwave.data.protected = True
    newwave.data.owner = event.userhost
    newwave.save()
    event.reply("done")

cmnds.add('wave-start', handle_wavestart, 'USER')
examples.add('wave-start', 'start a new wave', 'wave-start')

## wave-clone commnad

def handle_waveclone(bot, event):
    """ clone wave into a new one, copying over particpants and feeds. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return

    wave = event.chan
    event.reply("cloning ...")
    newwave = wave.clone(bot, event, event.root.title.strip(), True)
    if not newwave:
        event.reply("can't create new wave")
        return
    plugs.load('jsb.plugs.common.hubbub')
    feeds = plugs['jsb.plugs.common.hubbub'].watcher.clone(bot.name, bot.type, newwave.data.waveid, event.waveid)
    event.reply("this wave is continued to %s with the following feeds: %s" % (newwave.data.url, feeds))

cmnds.add('wave-clone', handle_waveclone, 'USER')
examples.add('wave-clone', 'clone the wave', 'wave-clone')

## wave-new command

def handle_wavenew(bot, event):
    """ make a new wave. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return

    parts = ['jsb@appspot.com', event.userhost]
    newwave = bot.newwave(event.domain, parts)

    if event.rest:
        newwave.SetTitle(event.rest)

    event.done()

cmnds.add('wave-new', handle_wavenew, 'USER')
examples.add('wave-new', 'make a new wave', 'wave-new')

## wave-public command

def handle_wavepublic(bot, event):
    """ make the wave public. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return

    event.root.participants.add('public@a.gwave.com')
    event.done()

cmnds.add('wave-public', handle_wavepublic, 'USER')
examples.add('wave-public', 'make the wave public', 'wave-public')

## wave-invite command

def handle_waveinvite(bot, event):
    """ invite a user to the wave. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return

    if not event.rest:
        event.missing('<who>')
        return

    event.root.participants.add(event.rest)
    event.done()

cmnds.add('wave-invite', handle_waveinvite, 'USER')
examples.add('wave-invite', 'invite a user/bot into the wave', 'wave-invite bthate@googlewave.com')

## wave-id command

def handle_waveid(bot, event):
    """ get the id of the wave. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return
    event.reply(event.waveid)

cmnds.add('wave-id', handle_waveid, 'USER')
examples.add('wave-id', 'show the id of the wave the command is given in.', 'wave-id')

## wave-url command

def handle_waveurl(bot, event):
    """ get the url of the wave. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return
    event.reply(event.url)

cmnds.add('wave-url', handle_waveurl, 'USER')
examples.add('wave-url', 'show the url of the wave the command is given in.', 'wave-url')

## wave-participants command

def handle_waveparticipants(bot, event):
    """ show participants. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return
    event.reply("participants: ", list(event.root.participants))

cmnds.add('wave-participants', handle_waveparticipants, 'USER')
examples.add('wave-participants', 'show the participants of the wave the command is given in.', 'wave-participants')

## wave-part command

def handle_wavepart(bot, event):
    """ leave a wave. not implemented yet. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return

    event.reply('bye')

cmnds.add('wave-part', handle_wavepart, 'OPER')
examples.add('wave-part', 'leave the wave', 'wave-part')

## wave-title ocmmand

def handle_wavetitle(bot, event):
    """ set title of the wave. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return

    if not event.rest:
        event.missing("<title>")
        return

    event.set_title(event.rest)
    event.reply('done')

cmnds.add('wave-title', handle_wavetitle, 'OPER')
examples.add('wave-title', 'set title of the wave', 'wave-title')

## wave-data command

def handle_wavedata(bot, event):
    """ show stored wave data. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return

    wave = event.chan
    if wave:
        data = dict(wave.data)
        del data['passwords']
        del data['json_data']
        event.reply(str(data))
    else:
        event.reply("can't fetch wave data of wave %s" % wave.waveid)

cmnds.add('wave-data', handle_wavedata, 'OPER')
examples.add('wave-data', 'show the waves stored data', 'wave-data')

## wave-threshold command

def handle_wavethreshold(bot, event):
    """ set threshold of the wave. after x nr of blips the wave will be cloned. """
    if event.bottype != "wave":
        event.reply("this command only works in google wave.");
        return

    try:
        nrblips = int(event.rest)
    except ValueError:
        nrblips = -1

    wave = event.chan
    if wave:
        if nrblips == -1:
            event.reply('threshold of "%s" is %s' % (wave.data.title, str(wave.data.threshold)))
            return
        wave.data.threshold = nrblips
        wave.save()
        event.reply('threshold of "%s" set to %s' % (wave.data.title, str(wave.data.threshold)))

cmnds.add('wave-threshold', handle_wavethreshold, 'OPER')
examples.add('wave-threshold', 'set nr of blips after which we clone the wave', 'wave-threshold')

## wave-whitelist command

def handle_wavewhitelistadd(bot, event):
    """ add a user to the waves whitelist .. allow modifications. """
    if not event.rest:
        event.missing("<id>")
        return

    target = event.rest
    if not event.chan.data.whitelist:
        event.chan.data.whitelist = []
    if target not in event.chan.data.whitelist:
        event.chan.data.whitelist.append(target)
        event.chan.save()
    event.reply("done")

cmnds.add("wave-whitelistadd", handle_wavewhitelistadd, "OPER")
examples.add("wave-whitelistadd", "add a user to the waves whitelist", "wave-whitelistadd bthate@googlewave.com")

## wave-whitelistdel command

def handle_wavewhitelistdel(bot, event):
    """ remove user from the waves whitelist .. deny modifications. """
    if not event.rest:
        event.missing("<id>")
        return

    target = event.rest
    if not event.chan.data.whitelist:
        event.chan.data.whitelist = []
    if target in event.chan.data.whitelist:
        event.chan.data.whitelist.remove(target)
        event.chan.save()
    event.reply("done")

cmnds.add("wave-whitelistdel", handle_wavewhitelistdel, "OPER")
examples.add("wave-whitelistdel", "delete a user from the waves whitelist", "wave-whitelistdel bthate@googlewave.com")
