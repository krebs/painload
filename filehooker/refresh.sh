#!/bin/sh

cd "$(dirname "$(readlink -f "$0")")"
rm -rvf  out/ work
./build.sh -N filehooker
cp -v out/filehooker* /home/makefu/isos
