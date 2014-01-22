# Running torrents through socks
## Prereqs:
- qBittorrent
- winswitch (xpra) or qbittorrent-nox

## Install
### Winswitch
see http://winswitch.org/downloads/debian-repository.html

## Autostart (xpra)

    # in startup script:
    export DISPLAY=:11
    xpra start $DISPLAY
    tmux start-server
    tmux new-window -t tools:1  'ssh -q -D1234 <remote-host>'
    tmux new-window -t tools:2 'qbittorrent'
    # attach to it:
    xpra attach ssh:omo:11

## Autostart (nox)
see https://github.com/qbittorrent/qBittorrent/wiki/Running-qBittorrent-without-X-server

## Lessons learned
- transmission sucks (no proxy support
