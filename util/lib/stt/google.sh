#!/bin/sh

cat <<EOF >&2
NOTE: The google speech-to-text api v1 has been made obsolete!
Code is here only for reference and will most likely not work anymore.
EOF

_get_content_type(){
    file -b --mime-type "$1"
}
_get_audio_rate(){
    file "$1" | sed -n -e 's/.* \([.0-9]\+\) kHz.*/\1/p' \
        | awk '{print int($1 *1000)}'
}

record_audio(){
    # usage : _record_audio num_seconds
    # echoes the output file
    tmpfile=$(mktemp)
    : ${1?please provide number of seconds to record}
    arecord -d "$1" -r 16000 -t wav -q -f cd  | flac -s -f - -o "$tmpfile" && echo "$tmpfile"
}
stt(){
    # usage: (lang=de-de stty recorded_file)
    : ${1? please provide recorded file}
    infile="$1"
    lang=${lang:-en-us}
    _get_content_type "$1" | (! grep -q "x-flac" ) \
        && echo "infile needs to be in flac format" \
        && return 1
    # only flac seems to be working...
    wget -q -O - \
        -U 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7' \
        --post-file "$infile"  \
        --header "Content-Type: `_get_content_type $infile`; rate=`_get_audio_rate $infile`;" \
    "http://www.google.com/speech-api/v1/recognize?lang=${lang}&client=chromium&maxresults=1" \
    | sed -n 's/.*utterance":"\([^"]*\)".*/\1/p'

    # returns {"status":0,"id":"d9269e6f741997161e41a4d441b34ba1-1","hypotheses":[{"utterance":"hallo Welt","confidence":0.7008959}]}
}
