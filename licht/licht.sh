#!/bin/bash
LAMPE="$1"
TOGGLE="$2"
LAMP=~s/[a-zA-Z]//g
TOGGLE=~s/[a-zA-Z]//g
STRING="\xA5\x5A\d$LAMPE\d$TOGGLE"
if [ $# != 2 ]
then
    echo -ne "Usage: licht <lampe> <0/1>"
else
    echo "$LAMPE$TOGGLE" 
    echo -ne "$STRING" | nc -u -w1 10.42.3.100 1337
fi
