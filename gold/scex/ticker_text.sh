#! /bin/sh
set -euf
cd $(dirname `readlink -f $0`)
./ticker | ../json/render/ticker
