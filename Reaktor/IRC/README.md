# //Reaktor/IRC

This component implements a remote shell daemon that exposes the
executable files (which may be symlinks) below
`//Reaktor/public_commands/` through IRC.

## Security

Access to the IRC server implies full access to all the exposed executable
files.  The daemon is executing the commands without dropping privileges.

## Quickstart

    #? /bin/sh
    set -euf

    export nick="$LOGNAME|$HOSTNAME"
    export host=irc.freenode.org
    export target='#tincspasm'

    exec Reaktor/IRC/index

## Environment variables

The following environment variables are processed by `//Reaktor/IRC`:

### nick

Use a specific nickname.

Optional if the node running `//Reaktor/IRC` is part of Retiolum, in
which case it defaults to `Name` in `/etc/tinc/retiolum/tinc.conf`.

### host and port

Connect to a specific IRC server.

Optional if the node running `//Reaktor/IRC` is part of Retiolum, in
which case it defaults to `supernode` and `6667` (well, it always
defaults to these two, but they only make science in Retiolum^_^).

### target

Join a specific channel.

As always, this does the right thing for properly configured hosts: it
uses the default `#retiolum`, which is the only really relevant
channel.^_^

