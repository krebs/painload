#! /bin/bash
#### anonbox.net - anonbox account creator
set -euf

## 
script_begin_date="`date --rfc-3339=ns`"

##
GET() {
  wget --quiet --no-check-certificate -O- https://anonbox.net/en/
}

## retrieve data
eval "$(${GET-GET} |
  sed -rn '
s^<dd><p>([[:alnum:]@.]+)</p></dd>$\
      email="\1" ; p
s^<dd><p><a href="([^"\\]+)">.*</a></p></dd>$\
      uri="\1" ; p
s^<dd><p>([0-9]+)/([0-9]+)/([0-9]+) ([0-9]+):([0-9]+) ([ap]).m.</p></dd>$\
      Y=20\3 ; \
      m=\1 ; \
      d=\2 ; \
      H=\4 ; \
      M=\5 ; \
      p=\6 ; p')"

## make best-before-date RFC-3339-(seconds)-conform
case "$p" in
  p) H="`echo $H+12 | bc`" ;;
esac
s=00
z=+02:00
best_before="$Y-$m-$d $H:$M$z"

##
script_end_date="`date --rfc-3339=ns`"

##
for key in email uri best_before script_begin_date script_end_date ; do
  eval "val=\"\$$key\""
  echo "$key	$val"
done

#### end of file.
