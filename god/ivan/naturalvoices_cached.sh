#!/bin/sh
# The cached version of naturalvoices
# This should prevent us from being pwned again ...

text=$(echo $* | sed -e 's/ /+/g' -e 's/\//%2F/g')
voice="klara"
ip=192.20.225.36
base_url="http://$ip"
CACHE_DIR="/tmp/ivan-speech"
mkdir -p $CACHE_DIR
TXTFILE="$CACHE_DIR/${text}.wav"
if [ ! -e $TXTFILE ] ;then
    echo "Downloading $TXTFILE"
    wget $base_url$( curl  -Ss  -H 'Host:$ip' \
  -H 'Origin:http://www2.research.att.com' \
  -e "http://www2.research.att.com/~ttsweb/tts/demo.php" \
  -A "Mozilla/5.0 (X11; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0" \
  -d "voice=$voice" -d "txt=$text" -d "speakButton=SPEAK" \
  -H 'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
      $base_url/tts/cgi-bin/nph-nvttsdemo | \
      grep HREF|sed 's/.*\(".*"\).*/\1/'  | \
      sed -e 's/"//g' ) -O "$TXTFILE" 2>/dev/null
else
    echo "using cached version of $TXTFILE"
fi
aplay "$TXTFILE"
