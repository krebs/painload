#! /bin/sh
esudo() {
  if test "${esudo-true}" = true -a `id -u` != 0; then
    echo "we're going sudo..." >&2
    export esudo=false
    exec sudo "$0" "$@"
    exit 23 # go to hell
  fi
}

