# streams done right(tm)

There are numerous ways to start streams ( make your computer or some server 
output streamed audio). Currently implemented are:

# Streams Modules
1. pure streams  - will start mpd on your local machine
2. mpdstreams    - will use a given mpd server to start a stream
3. relaxxstreams - will contact the relaxxplayer (mpd front-end) if the direct 
                   connection to the mpd is prohibited by firewall rules
# Database
Currently there are a number of possible streams saved in the database files
which contain of a link, a space, and the name of the stream. the database 
can be found in db/ .

Currently there are two kinds of databases:
1. streams.db - contains links to playlists of streams
2. direct.db  - contains links directly to the stream, not the playlist

to generate direct.db from a list of playlists use the helper/* scripts

# initscripts

the most convenient way to start streams is to use stream-starter which is 
a script which, when symlinked with a name of a stream, invokes the streams
tool with its own name as parameter.

An example:

    ln -s /krebs/god/streams/bin/stream-starter /etc/init.d/groove
    /etc/init.d/groove start

# Remarks
deepmix,groovesalad and radiotux are now init.d scrips which can be
started and stopped.

scripts are dumped into /etc/init.d and groovesalad will be set as
default via update-rc.d
