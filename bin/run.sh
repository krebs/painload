#!/bin/bash
echo basedir $0
BINDIR="`dirname $0`/../src"

python2 "$BINDIR/main.py" $@
