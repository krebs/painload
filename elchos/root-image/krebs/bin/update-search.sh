#!/bin/sh
for i in /media/vag*;do
  updatedb  -l 0 -o "$i/mlocate.db" -U "$i"
done
echo "update complete"
