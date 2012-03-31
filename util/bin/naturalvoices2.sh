text=$(echo $* | sed 's/ /+/g')
mplayer http://192.20.225.36$( curl -Ss -A "Mozilla" -d "voice=klara" -d "txt=$text" -d "speakButton=SPEAK" http://192.20.225.36/tts/cgi-bin/nph-nvdemo |grep HREF|sed 's/.*\(".*"\).*/\1/' |sed -e 's/"//g')

