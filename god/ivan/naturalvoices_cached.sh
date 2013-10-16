#!/bin/sh
# The cached version of naturalvoices
# This should prevent us from being pwned again ...

. ../../util/lib/naturalvoices/att.sh

: ${1?what to say?Please provide text as parameter.}

text=$(echo $* | sed -e 's/ /+/g' -e 's/\//%2F/g')
voice="${voice:-klara}"


CACHE_DIR="${CACHE_DIR:-/tmp/ivan-speech}"
mkdir -p "$CACHE_DIR"
OUTFILE="$CACHE_DIR/${voice}_${text}.wav"


if [ ! -e $OUTFILE ] ;then
    echo "Downloading $OUTFILE"
    get_tts "$text"
else
    echo "using cached version of $OUTFILE"
fi

play_file "$OUTFILE"
