#! /bin/sh
set -euf
cd $(dirname `readlink -f $0`)
./mtgox.ticker | ../json/render/ticker
