#! /bin/sh
set -euf
trap "echo 'You are made of stupid!' >&2; exit 23" EXIT
disarm() {
  trap - EXIT
}

COBRA_PATH="${COBRA_PATH-$PWD}"

## main
for target; do
  for path in $COBRA_PATH; do
    if test -d "$path/$target"; then
      if index="$path/$target/index.sh" && test -f "$index"; then
        exec /bin/sh "$index"
        disarm
      fi
    fi
  done
done
