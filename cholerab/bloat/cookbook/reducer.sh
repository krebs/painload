#! /bin/sh
# TODO tolower
tr '[:upper:]' '[:lower:]' |
sed '
  s/\<dosen\?//g
  s/mark//g
'
