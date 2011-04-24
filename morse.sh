#! /bin/sh
set -euf

freq=2000
dit=60
mode=compile+execute

while test $# -gt 0; do
  case "$1" in
    (-l) dit=$2; shift 2;;
    (-f) freq=$2; shift 2;;
    (-c) mode=compile; shift 1;;
    (-x) mode=execute; shift 1;;
    (*) break 2;;
  esac
done

# Ein Dah ist dreimal so lang wie ein Dit.
dah=`echo "$dit * 3" | bc`

char2morse() {
tr [a-z] [A-Z] |
sed '
  # Die Pause zwischen Wörtern beträgt sieben Dits. (1/2)
  s:[[:space:]]\+::g

  # Zwischen Buchstaben in einem Wort wird eine Pause von Dah eingeschoben.
  s:[^ ]:&   :g

  # Die Pause zwischen Wörtern beträgt sieben Dits. (2/2)
  s:   :       :g
' |
sed '
  # Lateinische Buchstaben
  # Die Pause zwischen zwei gesendeten Symbolen ist ein Dit lang.
  s:A:· −:g
  s:B:− · · ·:g
  s:C:− · − ·:g
  s:D:− · ·:g
  s:E:·:g
  s:F:· · − ·:g
  s:G:− − ·:g
  s:H:· · · ·:g
  s:I:· ·:g
  s:J:· − − −:g
  s:K:− · −:g
  s:L:· − · ·:g
  s:M:− −:g
  s:N:− ·:g
  s:O:− − −:g
  s:P:· − − ·:g
  s:Q:− − · −:g
  s:R:· − ·:g
  s:S:· · ·:g
  s:T:−:g
  s:U:· · −:g
  s:V:· · · −:g
  s:W:· − −:g
  s:X:− · · −:g
  s:Y:− · − −:g
  s:Z:− − · ·:g
' |
sed '
  # Ziffern
  # Die Pause zwischen zwei gesendeten Symbolen ist ein Dit lang.
  s:0:− − − − −:g
  s:1:· − − − −:g
  s:2:· · − − −:g
  s:3:· · · − −:g
  s:4:· · · · −:g
  s:5:· · · · ·:g
  s:6:− · · · ·:g
  s:7:− − · · ·:g
  s:8:− − − · ·:g
  s:9:− − − − ·:g
' |
sed '
  # TODO Sonder- und Satzzeichen
  #s:À, Å:· − − · −
  #s:Ä:· − · −
  #s:È:· − · · −
  #s:É:· · − · ·
  #s:Ö:− − − ·
  #s:Ü:· · − −
  #s:ß:· · · − − · ·
  #s:CH:− − − −
  #s:Ñ:− − · − −
  #s:. (AAA)	· − · − · −
  #s:, (MIM)	− − · · − −
  #s::	− − − · · ·
  #s:;	− · − · − ·
  #s:? (IMI)	· · − − · ·
  #s:-	− · · · · −
  #s:_	· · − − · −
  #s:(	− · − − ·
  #s:)	− · − − · −
  #s:'\''	· − − − − ·
  #s:=	− · · · −
  #s:+	· − · − ·
  #s:/	− · · − ·
  #s:@ (AC)	· − − · − ·
' |
sed '
  # TODO Signale
  # KA
  # (Spruchanfang)	− · − · −
  # BT
  # (Pause)	− · · · −
  # AR
  # (Spruchende)	· − · − ·
  # VE
  # (verstanden)	· · · − ·
  # SK
  # (Verkehrsende)	· · · − · −
  # SOS
  # (internationaler
  # (See-)Notruf)	· · · − − − · · ·
  # HH
  # (Fehler; Irrung;
  # Wiederholung
  # ab letztem
  # vollständigen Wort)	· · · · · · · ·
'
}

morse2beeparg() {
sed "
  s: : -n -f 1 -l $dit:g
  s:·: -n -f $freq -l $dit:g
  s:−: -n -f $freq -l $dah:g
" |
 sed '
  1s:^:beep -f 1 -l 1:
'
}

compile() {
  char2morse
}

execute() {
  `morse2beeparg`
}


if test $# -gt 0; then
  echo "$*"
else
  cat
fi |
case "$mode" in
  (compile) compile;;
  (execute) execute;;
  (compile+execute) compile | execute;;
  (*) echo bad mode: $mode >&2; exit 23;;
esac
