# jsb/plugs/socket/mpd.py
#
#
# interact with (your) Music Player Daemon
# (c) Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License
#
# CHANGELOG
#  2011-02-20
#   * sMiLe - changed methods to be similar to the mpc commands
#  2011-02-13
#   * sMiLe - added several new functions
#  2011-01-16
#   * BHJTW - adapted to jsonbot
#  2008-10-30
#   * fixed "Now playing" when having a password on MPD
#  2007-11-16
#   * added watcher support
#   * added formatting options ('song-status')
#   * added more precision to duration calculation
#  2007-11-10
#   * initial version
#
# REFERENCES
#
#  The MPD wiki is a great resource for MPD information, especially:
#   * http://mpd.wikia.com/wiki/MusicPlayerDaemonCommands
#

""" music player daemon control. """

__version__ = '2007111601'


## jsb imports

from jsb.lib.commands import cmnds
from jsb.lib.datadir import getdatadir
from jsb.lib.examples import examples
from jsb.lib.fleet import fleet
from jsb.utils.pdod import Pdod
from jsb.lib.persistconfig import PersistConfig
from jsb.lib.threads import start_new_thread

## basic imports

import os
import socket
import time

## defines

cfg = PersistConfig()
cfg.define('server-host', '127.0.0.1')
cfg.define('server-port', 6600)
cfg.define('server-pass', '')
cfg.define('socket-timeout', 15)
cfg.define('watcher-interval', 10)
cfg.define('watcher-enabled', 0)
cfg.define('song-status', 'now playing: %(artist)s - %(title)s on "%(album)s" (duration: %(time)s)')

## classes

class MPDError(Exception):
    """ exception to raise. """
    pass

class MPDDict(dict):
    """ return ? on no existant entry. """
    def __getitem__(self, item):
        if not dict.has_key(self, item):
            return '?'
        else:
            return dict.__getitem__(self, item)

class MPDWatcher(Pdod):
    """ the MPD watcher. """
    def __init__(self):
        Pdod.__init__(self, os.path.join(getdatadir() + os.sep + 'plugs' + os.sep + 'jsb.plugs.sockets.mpd', 'mpd'))
        self.running = False
        self.lastsong = -1

    def add(self, bot, ievent):
        """ add a watcher. """
        if not self.has_key2(bot.cfg.name, ievent.channel):
            self.set(bot.cfg.name, ievent.channel, True)
            self.save()

    def remove(self, bot, ievent):
        """ remove a watcher. """
        if self.has_key2(bot.cfg.name, ievent.channel):
            del self.data[bot.cfg.name][ievent.channel]
            self.save()

    def start(self):
        """ start the watcher. """
        self.running = True
        start_new_thread(self.watch, ())

    def stop(self):
        """ stop the watcher. """
        self.running = False

    def watch(self):
        """ do the actual watching. """
        if not cfg.get('watcher-enabled'):
            raise MPDError('watcher not enabled, use "!%s-cfg watcher-enabled 1" to enable' % os.path.basename(__file__)[:-3])
        while self.running:
            if self.data:
                try:
                    status = MPDDict(mpd('currentsong'))
                    songid = int(status['id'])
                    if songid != self.lastsong:
                        self.lastsong = songid
                        self.announce(status)
                except MPDError:
                    pass
                except KeyError:
                    pass
            time.sleep(cfg.get('watcher-interval'))

    def announce(self, status):
        """ announce a new status. """
        if not self.running or not cfg.get('watcher-enabled'):
            return
        status['time'] = mpd_duration(status['time'])
        song = cfg.get('song-status') % status
        for name in self.data.keys():
            bot = fleet.byname(name)
            if bot:
                for channel in self.data[name].keys():
                    bot.say(channel, song)

## init

watcher = MPDWatcher()
if not watcher.data:
    watcher = MPDWatcher()

def init():
    if cfg.get('watcher-enabled'):
        watcher.start()
    return 1

def shutdown():
    if watcher.running:
        watcher.stop()
    return 1

## mpd-function

def mpd(command):
    """ do a MPD command. """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(cfg.get('socket-timeout'))
        s.connect((cfg.get('server-host'), cfg.get('server-port')))
    except socket.error, e:
        raise MPDError, 'Failed to connect to server: %s' % str(e)
    m = s.makefile('r')
    l = m.readline()
    if not l.startswith('OK MPD '): s.close() ; raise MPDError, 'Protocol error'
    if cfg.get('server-pass') and cfg.get('server-pass') != 'off':
        s.send('password %s\n' % cfg.get('server-pass'))
        l = m.readline()
        if not l.startswith('OK'):
            s.close()
            raise MPDError, 'Protocol error'
    s.send('%s\n' % command)
    s.send('close\n')
    d = []
    while True:
        l = m.readline().strip()
        if not l or l == 'OK':
            break
        if ': ' in l:
            l = l.split(': ', 1)
            l[0] = l[0].lower()
            d.append(tuple(l))
    s.close()
    return d

def mpd_duration(timespec):
    """ return duration string. """
    try:
        timespec = int(timespec)
    except ValueError:
        return 'unknown'
    timestr  = ''
    m = 60
    h = m * 60
    d = h * 24
    w = d * 7
    if timespec > w:
        w, timespec = divmod(timespec, w)
        timestr = timestr + '%02dw' % w
    if timespec > d:
        d, timespec = divmod(timespec, d)
        timestr = timestr + '%02dd' % d
    if timespec > h:
        h, timespec = divmod(timespec, h)
        timestr = timestr + '%02dh' % h
    if timespec > m:
        m, timespec = divmod(timespec, m)
        timestr = timestr + '%02dm' % m
    return timestr + '%02ds' % timespec

## mpd command

def handle_mpd(bot, ievent):
    """ no arguments - display mpd status. """
    try:
        result = []
        song = MPDDict(mpd('currentsong'))
        status = MPDDict(mpd('status'))
        status['time'] = mpd_duration(status['time'])
        reply = ''
        if status['state'] == 'play': 
            status['state'] = 'playing'
            reply += '%s: %s\n[%s] #%s/%s %s (%s)\n' % (song['name'], song['title'], status['state'], status['song'], status['playlistlength'], status['time'], '0')
        if status['state'] == 'stop': status['state'] = 'stopped'
        reply += 'volume: %s | repeat: %s | random: %s | single: %s | consume: %s' % (status['volume'], status['repeat'], status['random'], status['single'], status['consume'])
        ievent.reply(reply)
    except MPDError, e: ievent.reply(str(e))

#mpd                                           Display status
cmnds.add('mpd', handle_mpd, 'USER', threaded=True)
examples.add('mpd', 'Display mpd status', 'mpd')

## mpd-outputs command

def handle_mpd_outputs(bot, ievent):
    """ show mpd outputs. """
    # Output 1 (My ALSA Device) is enabled
    # [('outputid', '0'), ('outputname', 'My ALSA Device'), ('outputenabled', '1')]
    try:
        outputs = mpd('outputs')
        outputid = '?'
        outputname = '?'
        outputenabled = '?'
        result = []
        for item in outputs:
            if item[0] == 'outputid': outputid = int(item[1])+1
            if item[0] == 'outputname': outputname = item[1]
            if item[0] == 'outputenabled':
                if item[1] == '1': outputenabled = 'enabled' 
                else: outputenabled = 'disabled'
                result.append('Output %d (%s) is %s' % (outputid, outputname, outputenabled))
                outputid = '?'
                outputname = '?'
                outputenabled = '?'
        ievent.reply("\n".join(result))
    except MPDError, e:
        ievent.reply(str(e))

## mpd-enable command

def handle_mpd_enable(bot, ievent):
    """ arguments: <outputnumber> - enable an output. """
    try:
        try: output = int(ievent.args[0])-1
        except: ievent.missing('<output #>') ; return
        result = mpd('enableoutput %d' % output)
        ievent.reply(result)
    except MPDError, e:
        ievent.reply(str(e))

## mpd-disable command

def handle_mpd_disable(bot, ievent):
    """ arguments: <outputnumber> - disable an output. """
    try:
        try: output = int(ievent.args[0])-1
        except: ievent.missing('<output #>') ; return
        result = mpd('disableoutput %d' % output)
        ievent.reply(result)
    except MPDError, e:
        ievent.reply(str(e))

## mpd-playlist command

def handle_mpd_playlist(bot, ievent):
    """ no arguments - show playlist. """
    try:
        playlist = mpd('playlistinfo')
        tmp = ''
        result = []
        for item in playlist:
           if item[0] == 'file': 
              if not tmp == '': result.append(tmp)
              tmp = item[1]
           if item[0] == 'title': tmp = item[1]
           if item[0] == 'name': tmp = '%s: %s' % (item[1], tmp)
        ievent.reply("\n".join(result))
    except MPDError, e:
        ievent.reply(str(e))

## mpd-lsplaylists command

def handle_mpd_lsplaylists(bot, ievent):
    """ no arguments - show playlists. """
    try:
        playlists = mpd('lsinfo')
        result = []
        for item in playlists:
           if item[0] == 'playlist': 
              result.append(item[1])
        ievent.reply("\n".join(result))
    except MPDError, e:
        ievent.reply(str(e))

## mpd-playlistmanipulation command

def handle_mpd_playlist_manipulation(bot, ievent, command):
    """ arguments: <playlist> - manipulate a playlist, the command is given as parameter """
    try:
        if not ievent.args:
            ievent.missing('<playlist>')
            return
        playlist = str(ievent.args[0])
        result = mpd('%s %s' % (command, playlist))
        ievent.reply('Playlist %s loaded.' % playlist)
    except MPDError, e:
        ievent.reply(str(e))

## mpd-load command

def handle_mpd_load(bot, ievent):
     """ arguments: <playlist> - load playlist. """
     handle_mpd_playlist_manipulation(bot, ievent, 'load')

## mpd-save command

def handle_mpd_save(bot, ievent):
     """ arguments: <playlist> - save playlist. """
     handle_mpd_playlist_manipulation(bot, ievent, 'save')

## mpd-rm command

def handle_mpd_rm(bot, ievent):
     """ arguments: <playlist> - remove playlist. """
     handle_mpd_playlist_manipulation(bot, ievent, 'rm')

## mpd-np command

def handle_mpd_np(bot, ievent):
    """ no arguments - show current playing song. """
    try:
        status = MPDDict(mpd('currentsong'))
        status['time'] = mpd_duration(status['time'])
        ievent.reply(cfg.get('song-status') % status)
    except MPDError, e:
        ievent.reply(str(e))

#mpd-current                                   Show the currently playing song
cmnds.add('mpd-current',    handle_mpd_np,    'USER', threaded=True)
cmnds.add('mpd-np',    handle_mpd_np,    'USER', threaded=True)
examples.add('mpd-current', 'Show the currently playing song', 'mpd-current')

## mpd-simpleseek command

def handle_mpd_simple_seek(bot, ievent, command):
    """ no arguments - do a seek. """
    try:
        mpd(command)
        #handle_mpd_np(bot, ievent)
        handle_mpd(bot, ievent)
    except MPDError, e:
        ievent.reply(str(e))

## mpd-next command

handle_mpd_next = lambda b,i: handle_mpd_simple_seek(b,i,'next') 

#mpd-next                                      Play the next song in the current playlist
cmnds.add('mpd-next',  handle_mpd_next,  'MPD', threaded=True)
examples.add('mpd-next', 'play the next song in the current playlist', 'mpd-next')

## mpd-prev command

handle_mpd_prev = lambda b,i: handle_mpd_simple_seek(b,i,'prev') 

#mpd-prev                                      Play the previous song in the current playlist
cmnds.add('mpd-prev',  handle_mpd_prev,  'MPD', threaded=True)
examples.add('mpd-prev', 'play the previous song in the current playlist', 'mpd-prev')

## mpd-play command

handle_mpd_play = lambda b,i: handle_mpd_simple_seek(b,i,'play') 

#mpd-play [<position>]                         Start playing at <position> (default: 1)
cmnds.add('mpd-play',  handle_mpd_play,  'MPD', threaded=True)
examples.add('mpd-play', 'start playing at <position> (default: 1)', 'mpd-play')

## mpd-stop command

handle_mpd_stop = lambda b,i: handle_mpd_simple_seek(b,i,'stop') 

## mpd-pause command

handle_mpd_pause = lambda b,i: handle_mpd_simple_seek(b,i,'pause') 

#mpd-pause                                     Pauses the currently playing song
cmnds.add('mpd-pause', handle_mpd_pause, 'MPD', threaded=True)
examples.add('mpd-pause', 'pauses the currently playing song', 'mpd-pause')

## mpd-clear command

handle_mpd_clear = lambda b,i: handle_mpd_simple_seek(b,i,'clear') 

## mpd-crop command

handle_mpd_crop = lambda b,i: handle_mpd_simple_seek(b,i,'crop') 

#mpd-crop                                      Remove all but the currently playing song
cmnds.add('mpd-crop', handle_mpd_crop, 'MPD', threaded=True)
examples.add('mpd-crop', 'remove all but the currently playing song', 'mpd-crop')

## mpd-shuffle command

handle_mpd_shuffle = lambda b,i: handle_mpd_simple_seek(b,i,'shuffle') 

## mpd-repeat command

handle_mpd_repeat = lambda b,i: handle_mpd_toggle_option(b,i,'repeat') 

## mpd-random command

handle_mpd_random = lambda b,i: handle_mpd_toggle_option(b,i,'random') 

## mpd-single command

handle_mpd_single= lambda b,i: handle_mpd_toggle_option(b,i,'single') 

## mpd-consume command

handle_mpd_consume= lambda b,i: handle_mpd_toggle_option(b,i,'consume') 

## mpd-crossfade command

handle_mpd_crossfade= lambda b,i: handle_mpd_set_option(b,i,'crossfade') 

## mpd-find command

def handle_mpd_find(bot, ievent):
    type = 'title'
    args = ievent.args
    if args and args[0].lower() in ['title', 'album', 'artist']: type = args[0].lower() ; args = args[1:]
    if not args: ievent.missing('[<type>] <what>') ; return
    try:
        find = mpd('search %s "%s"' % (type, ' '.join(args)))
        show = []
        for item, value in find:
            if item == 'file': show.append(value)
        if show: ievent.reply("results: ", show)
        else: ievent.reply('no result')
    except MPDError, e: ievent.reply(str(e))

## mpd-add command

def handle_mpd_add(bot, ievent):
    """ arguments: <filename> - add a file to the MPD. """
    if not ievent.args:
        ievent.missing('<filename>')
        return
    try:
        addid = MPDDict(mpd('addid "%s"' % ievent.rest))
        if not addid.has_key('id'):
            ievent.reply('failed to load song "%s"' % ievent.rest)
        else:
            ievent.reply('added song with id "%s", use "mpd-jump %s" to start playback' % (addid['id'], addid['id']))
    except MPDError, e:
        ievent.reply(str(e))

#mpd-add <file>                                Add a song to the current playlist
cmnds.add('mpd-add', handle_mpd_add, 'MPD', threaded=True)
cmnds.add('mpd-queue', handle_mpd_add, 'MPD', threaded=True)
examples.add('mpd-add', 'add a song to the current playlist', 'mpd-add mp3/bigbeat/fatboy slim/fatboy slim - everybody needs a 303.mp3')

## mpd-del command

def handle_mpd_del(bot, ievent):
    """ arguments: <position> - remove a song from the current playlist. """
    if not ievent.args: ievent.missing('<position>') ; return
    try: result = mpd('delete %d' % int(ievent.args[0])) ; ievent.reply(result)
    except MPDError, e: ievent.reply(str(e))

#mpd-del <position>                            Remove a song from the current playlist
cmnds.add('mpd-del',  handle_mpd_del,  'MPD', threaded=True)
examples.add('mpd-del', 'remove a song from the current playlist', 'mpd-del 1')

## mpd-jump command

def handle_mpd_jump(bot, ievent):
    """ arguments: <id> - jump to playlist. """
    pos = 0
    try:    pos = int(ievent.args[0])
    except: pass
    if not pos: ievent.missing('<playlist id>') ; return
    try:
        mpd('playid %d' % pos)
        handle_mpd_np(bot, ievent)
    except MPDError, e: ievent.reply(str(e))

cmnds.add('mpd-jump',  handle_mpd_jump, 'MPD', threaded=True)
examples.add('mpd-jump', 'jump to the specified playlist id', 'mpd-jump 777')

## mpd-stats command

def handle_mpd_stats(bot, ievent):
    """ no arguments - determine MPD stats. """
    try:
        status = MPDDict(mpd('stats'))
        status['total playtime'] = mpd_duration(status['playtime'])
        status['total database playtime'] = mpd_duration(status['db_playtime'])
        status['uptime'] = mpd_duration(status['uptime'])
        del status['playtime']
        del status['db_playtime']
        del status['db_update']
        result = []
        for item in sorted(status.keys()):
            result.append('%s: %s' % (item, status[item]))
        ievent.reply(" | ".join(result))
    except MPDError, e:
        ievent.reply(str(e))

#mpd-stats                                     Display statistics about MPD
cmnds.add('mpd-stats', handle_mpd_stats, 'USER', threaded=True)
examples.add('mpd-stats', 'Display statistics about MPD', 'mpd-stats')

## mpd-volume command

def handle_mpd_volume(bot, ievent):
    """ arguments: <volume> - set MPD volume. """
    volume = 0
    try:    volume = int(ievent.args[0])
    except: pass
    if not volume:
        status = MPDDict(mpd('status'))
        ievent.reply('Current volume: %s' % status['volume'])
        return        
    try:
        mpd('setvol %d' % volume)
        ievent.reply('Volume set to %d' % volume)
    except MPDError, e:
        ievent.reply(str(s))

## mpd-toggleoption command

def handle_mpd_toggle_option(bot, ievent, option):
    """ arguments: <value> - toggle variable. """
    if ievent.args:
        val = 'on'
        try:    val = ievent.args[0]
        except: pass
        if val == '0' or val == 'off': val = '0'
        else: val = '1'
    else:
        status = MPDDict(mpd('status'))
        if status[option] == '0': val = '1'
        else: val = '0'
    try:
        mpd('%s %s' % (option, val))
        handle_mpd(bot, ievent)
    except MPDError, e:
        ievent.reply(str(e))

## mpd-setoption command

def handle_mpd_set_option(bot, ievent, option):
    """ arguments: <value> - set value of an option. """ 
    try:
        if ievent.args:
            val = -1
            try:    val = int(ievent.args[0])
            except: pass
            if val > 0: 
                mpd('%s %s' % (option, val))
            
            else: 
                ievent.reply('"off" is not 0 or positive integer' % ievent.args[0])
                return
        else:
            status = MPDDict(mpd('status'))
            ievent.reply("%s %s" % (option, status['xfade']))
    except MPDError, e:
        ievent.reply(str(e))

## mpd-watchstart command

def handle_mpd_watch_start(bot, ievent):
    """ no arguments - start MPD watcher. """
    if not cfg.get('watcher-enabled'):
        ievent.reply('watcher not enabled, use "!%s-cfg watcher-enabled 1" to enable and reload the plugin' % os.path.basename(__file__)[:-3])
        return
    watcher.add(bot, ievent)
    ievent.reply('ok')

cmnds.add('mpd-watch-start', handle_mpd_watch_start, 'MPD', threaded=True)

## mpd-watchstop command

def handle_mpd_watch_stop(bot, ievent):
    """ no arguments - stop MPD watcher. """
    if not cfg.get('watcher-enabled'):
        ievent.reply('watcher not enabled, use "!%s-cfg watcher-enabled 1" to enable and reload the plugin' % os.path.basename(__file__)[:-3])
        return
    watcher.remove(bot, ievent)
    ievent.reply('ok')

cmnds.add('mpd-watch-stop',  handle_mpd_watch_stop, 'MPD', threaded=True)

## mpd-watchlist command

def handle_mpd_watch_list(bot, ievent):
    """ no aruguments - list the watchers channels. """
    if not cfg.get('watcher-enabled'):
        ievent.reply('watcher not enabled, use "!%s-cfg watcher-enabled 1" to enable and reload the plugin' % os.path.basename(__file__)[:-3])
        return
    result = []
    for name in sorted(watcher.data.keys()):
        if watcher.data[name]:
            result.append('on %s:' % name)
        for channel in sorted(watcher.data[name].keys()):
            result.append(channel)
    if result:
        ievent.reply(' '.join(result))
    else:
        ievent.reply('no watchers running')

cmnds.add('mpd-watch-list',  handle_mpd_watch_list, 'MPD', threaded=True)

## register command and exmaples

#mpd-toggle                                    Toggles Play/Pause, plays if stopped
cmnds.add('mpd-toggle', handle_mpd_pause, 'MPD', threaded=True)
examples.add('mpd-toggle', 'Toggles Play/Pause, plays if stopped', 'mpd-toggle')

#mpd-stop                                      Stop the currently playing playlists
cmnds.add('mpd-stop',  handle_mpd_stop,  'MPD', threaded=True)
examples.add('mpd-stop', 'Stop the currently playing playlists', 'mpd-stop')

# TODO mpd-seek [+-][HH:MM:SS]|<0-100>%              Seeks to the specified position
# cmnds.add('mpd-seek', handle_mpd_seek, 'MPD')
#mpd-clear                                     Clear the current playlist
cmnds.add('mpd-clear', handle_mpd_clear, 'MPD', threaded=True)
examples.add('mpd-clear', 'Clear the current playlist', 'mpd-clear')

#mpd-outputs                                   Show the current outputs
cmnds.add('mpd-outputs', handle_mpd_outputs, 'MPD', threaded=True)
examples.add('mpd-outputs', 'Show the current outputs', 'mpd-outputs')

#mpd-enable <output #>                         Enable a output
cmnds.add('mpd-enable', handle_mpd_enable, 'MPD', threaded=True)
examples.add('mpd-enable', 'Enable a output', 'mpd-enable <output #>')

#mpd-disable <output #>                        Disable a output
cmnds.add('mpd-disable', handle_mpd_disable, 'MPD', threaded=True)
examples.add('mpd-disable', 'Disable a output', 'mpd-disable <output #>')

#mpd-shuffle                                   Shuffle the current playlist
cmnds.add('mpd-shuffle', handle_mpd_shuffle, 'MPD', threaded=True)
examples.add('mpd-shuffle', 'Shuffle the current playlist', 'mpd-shuffle')

# TODO mpd move <from> <to>                          Move song in playlist
#cmnds.add('mpd-move', handle_mpd_move, 'MPD')
#examples.add('mpd-move', 'Move song in playlist', 'mpd-move <from> <to>')

#mpd-playlist                                  Print the current playlist
cmnds.add('mpd-playlist', handle_mpd_playlist, 'USER', threaded=True)
examples.add('mpd-playlist', 'Print the current playlist', 'mpd-playlist')

# TODO mpd listall [<file>]                          List all songs in the music dir
#cmnds.add('mpd-listall', handle_mpd_listall, 'USER')
#examples.add('mpd-listall', 'List all songs in the music dir', 'mpd-listall [<file>]')

# TODO mpd ls [<directory>]                          List the contents of <directory>
#cmnds.add('mpd-ls', handle_mpd_ls, 'USER')
#examples.add('mpd-ls', 'List the contents of <directory>', 'mpd-ls [<directory>]')

#mpd-lsplaylists                               List currently available playlists
cmnds.add('mpd-lsplaylists', handle_mpd_lsplaylists, 'USER', threaded=True)
examples.add('mpd-lsplaylists', 'List currently available playlists', 'mpd-lsplaylists')

#mpd-load <file>                               Load <file> as a playlist
cmnds.add('mpd-load', handle_mpd_load, 'MPD', threaded=True)
examples.add('mpd-load', 'Load <file> as a playlist', 'mpd-load <file>')

#mpd-save <file>                               Save a playlist as <file>
cmnds.add('mpd-save', handle_mpd_save, 'MPD', threaded=True)
examples.add('mpd-save', 'Save a playlist as <file>', 'mpd-save <file>')

#mpd-rm <file>                                 Remove a playlist
cmnds.add('mpd-rm', handle_mpd_rm, 'MPD', threaded=True)
examples.add('mpd-rm', 'Remove a playlist', 'mpd-rm <file>')

#mpd-volume [+-]<num>                          Set volume to <num> or adjusts by [+-]<num>
# TODO [+-]
cmnds.add('mpd-volume', handle_mpd_volume, 'MPD', threaded=True)
examples.add('mpd-volume', 'Set volume to <num> or adjusts by [+-]<num>', 'mpd-volume 42')

#mpd-repeat <on|off>                           Toggle repeat mode, or specify state
cmnds.add('mpd-repeat', handle_mpd_repeat, 'MPD', threaded=True)
examples.add('mpd-volume', 'Toggle repeat mode, or specify state', 'mpd-repeat off')

#mpd-random <on|off>                           Toggle random mode, or specify state
cmnds.add('mpd-random', handle_mpd_random, 'MPD', threaded=True)
examples.add('mpd-random', 'Toggle random mode, or specify state', 'mpd-random <on|off>')

#mpd-single <on|off>                           Toggle single mode, or specify state
cmnds.add('mpd-single', handle_mpd_single, 'MPD', threaded=True)
examples.add('mpd-single', 'Toggle single mode, or specify state', 'mpd-single <on|off>')

#mpd-consume <on|off>                          Toggle consume mode, or specify state
cmnds.add('mpd-consume', handle_mpd_consume, 'MPD', threaded=True)
examples.add('mpd-consume', 'Toggle consume mode, or specify state', 'mpd-consume <on|off>')

# TODO mpd search <type> <query>                     Search for a song
#cmnds.add('mpd-search', handle_mpd_search, 'MPD')
#examples.add('mpd-search', 'Search for a song', 'mpd-search <type> <query>')

#mpd-find <type> <query>                       Find a song (exact match)
cmnds.add('mpd-find',  handle_mpd_find,  'MPD', threaded=True)
examples.add('mpd-find', 'Find a song (exact match)', 'mpd-find title love')

# TODO mpd-findadd <type> <query>                    Find songs and add them to the current playlist
# cmnds.add('mpd-findadd', handle_mpd_findadd, 'MPD')
#examples.add('mpd-findadd', 'Find songs and add them to the current playlist', 'mpd-findadd <type> <query>')

# TODO mpd-list <type> [<type> <query>]              Show all tags of <type>
# cmnds.add('mpd-list', handle_mpd_list, 'MPD')
#examples.add('mpd-list', 'Show all tags of <type>', 'mpd-list <type> [<type> <query>]')

#mpd-crossfade [<seconds>]                     Set and display crossfade settings
cmnds.add('mpd-crossfade', handle_mpd_crossfade, 'MPD', threaded=True)
examples.add('mpd-crossfade', 'Set and display crossfade settings', 'mpd-crossfade 42')

#mpd-update [<path>]                           Scan music directory for updates
#cmnds.add('mpd-update', handle_mpd_update, 'MPD')

#mpd-sticker <uri> <get|set|list|del> <args..> Sticker management
#cmnds.add('mpd-sticker', handle_mpd_sticker, 'MPD')


#mpd-version                                   Report version of MPD
#cmnds.add('mpd-version', handle_mpd_version, 'USER')

#mpd-idle [events]                             Idle until an event occurs
#cmnds.add('mpd-idle', handle_mpd_idle, 'MPD')

#mpd-idleloop [events]                         Continuously idle until an event occurs
#cmnds.add('mpd-idleloop', handle_mpd_idleloop, 'MPD')

# TODO mpd-replaygain [off|track|ablum]              Set or display the replay gain mode
# cmnds.add('mpd-replaygain', handle_mpd_replaygain, 'MPD')
#examples.add('mpd-replaygain', 'Set or display the replay gain mode', 'mpd-replaygain')
