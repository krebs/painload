#!/bin/sh
text=$(echo $* | sed 's/ /+/g')
voice="klara"
base_url="http://192.20.225.36"

TMPFILE=`mktemp`
trap "rm $TMPFILE" TERM INT EXIT

 wget $base_url$( curl  -Ss  -H 'Host:192.20.225.36' -H 'Origin:http://www2.research.att.com' -e "http://www2.research.att.com/~ttsweb/tts/demo.php" -A "Mozilla/5.0 (X11; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0" -d "voice=$voice" -d "txt=$text" -d "speakButton=SPEAK" -H 'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' $base_url/tts/cgi-bin/nph-nvttsdemo | grep HREF|sed 's/.*\(".*"\).*/\1/'  |sed -e 's/"//g' ) -O $TMPFILE
aplay $TMPFILE
