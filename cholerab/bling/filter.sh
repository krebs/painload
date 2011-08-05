#! /bin/sh
set -euf
echo "[31;1m`cat "$1"`[m" | sed 's/x/[41m [m/g'
