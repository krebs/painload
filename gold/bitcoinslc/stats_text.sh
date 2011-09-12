#! /bin/sh
set -euf
cd $(dirname `readlink -f $0`)
./bitcoinslc.stats | ./bitcoinslc.stats.render
