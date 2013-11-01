#!/bin/sh
# The cached version of naturalvoices
# This should prevent us from being pwned again ...



get_tts(){
    # ENV:
    #   OUTFILE - path to outfile (required)
    #   voice   - voice to use (default: klara)
    # INP:
    #   $@      - input text

    : ${OUTFILE?please provide OUTFILE}
    text=$(echo $* | sed -e "s/ /+/g" -e "s/\//%2F/g")
    voice="${voice:-klara}"
    # TODO grab this url from the tts demo page
    ip="204.178.9.51"
    base_url="http://$ip"
    curl -sS $base_url$( curl  -Ss  -H "Host:$ip" \
        -H "Origin:http://www2.research.att.com" \
        -e "http://www2.research.att.com/~ttsweb/tts/demo.php" \
        -A "Mozilla/5.0 (X11; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0" \
        -d "voice=$voice" -d "txt=$text" -d "speakButton=SPEAK" \
        -H "Accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
            "$base_url/tts/cgi-bin/nph-nvttsdemo" | \
            grep HREF|sed 's/.*\(".*"\).*/\1/'  | \
            sed -e 's/"//g' ) > "$OUTFILE"
}

play_file(){
    aplay "$*" >/dev/null
}
