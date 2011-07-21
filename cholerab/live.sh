#! /bin/sh
set -euf
stty cbreak -echo

go() {
  state=$1
  wr 7
  wr "[1;70H             " >&2
  wr "[1;70Hstate=$state" >&2
  wr 8
  $1
}

rd() {
  dd bs=1 count=1 2>/dev/null
}

bufrd() {
  buf="`rd`"
  bufinfowr
}

bufrda() {
  buf="$buf`rd`"
  bufinfowr
}

bufinfowr() {
  wr 7
  wr "[2;70H          " >&2
  wr "[3;70H          " >&2
  case "$buf" in
    () wr '[2;70H[35m^[[m' >&2;;
    (*) wr "[2;70H$buf" >&2;;
  esac
  wr "[3;70H`wr "$buf" | xxd -p`" >&2
  wr 8
}

wr() {
  echo -n "$1"
}

C0="`echo C0 | xxd -r -p`"; DF="`echo DF | xxd -r -p`" 
E0="`echo E0 | xxd -r -p`"; EF="`echo EF | xxd -r -p`"
F0="`echo F0 | xxd -r -p`"; F7="`echo F7 | xxd -r -p`"
S() {
  bufrd
  case "$buf" in
    () go ESC;;
    () wr '[D [D'; go S;;
    ([$C0-$DF]) go U1;;
    ([$E0-$EF]) go U2;;
    ([$F0-$F7]) go U3;;
    (*) wr "$buf"; go S;;
  esac
}

U1() { buf="$buf`rd`"; wr "$buf"; go S; }
U2() { buf="$buf`rd`"; go U1; }
U3() { buf="$buf`rd`"; go U2; }


ESC() {
  bufrda
  case "$buf" in
    ('[') go ESC_OSQRB;;
    (*)
      wr '[35m^[[m'
      go S
      ;;
  esac
}

ESC_OSQRB() {
  bufrda
  case "$buf" in
    ('[A'|'[B'|'[C'|'[D') wr "$buf"; go S;;
    (*)
      wr '[35m^[[m['
      go S
      ;;
  esac
}


wr 'c'
go S
