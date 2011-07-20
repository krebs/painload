#! /bin/sh
set -euf
stty cbreak -echo

getc() {
  echo -n "7[1;70H             8" >&2
  echo -n "7[1;70Hstate=$state8" >&2
  set -- "`dd bs=1 count=1 2>/dev/null`"
  set -- "$1" "`echo -n "$1" | od -An -tx | tr -d "[$IFS]"`"
  char="$1"
  odchar="$2"
  echo -n "$1"
}

state() {
  state="$1"
  echo -n "7[1;70H             8" >&2
  echo -n "7[1;70Hstate=$state8" >&2
  char="`dd bs=1 count=1 2>/dev/null`"
  odchar="`echo -n "$char" | od -An -tx | tr -d "[$IFS]"`"
  history="$odchar  [10D[B${history-}"
  echo -n "7[2;70H          8" >&2
  echo -n "7[3;70H          8" >&2
  echo -n "7[4;70H`echo -n "$history"`8" >&2
}


S() {
  state S
  case "$char" in
    () ESC "$char";;
    () echo -n '[D [D'; S;;
    (*)
      echo -n "$char"
      S
      ;;
  esac
}

ESC() {
  state ESC
  case "$char" in
    ('[') ESC_OSQRB "$1$char";;
    (*)
      echo -n '[35m^[[m'
      S
      ;;
  esac
}

ESC_OSQRB() {
  state ESC_OSQRB
  case "$char" in
    (A|B|C|D) echo -n "$1$char"; S;;
    ('[') ESC_OSQRB2 "$1$char";;
    (*)
      echo -n '[35m^[[m['
      S
      ;;
  esac
}

ESC_OSQRB2() {
  state ESC_OSQRB2
  case "$char" in
    (A|B|C|D) echo -n "$1$char"; S;;
    (*)
      echo -n '[35m^[[m[['
      S
      ;;
  esac
}


echo -n 'c'
S
