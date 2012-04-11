text=$(echo $* | sed 's/ /+/g')
voice="klara"
base_url="http://192.20.225.36"

mplayer $base_url$( curl -Ss -A "Mozilla" -d "voice=$voice" -d "txt=$text" -d "speakButton=SPEAK" $base_url/tts/cgi-bin/nph-nvdemo |grep HREF|sed 's/.*\(".*"\).*/\1/' |sed -e 's/"//g')

