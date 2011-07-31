#! /bin/sh
set -euf

# TODO check json first

# XXX json_key is something like PWD^^

normalize_json() {
  sed -rn '
    1s/^/cat<<EOF\n/
    # TODO handle escaped double quotes
    s/"[^"]+"/"$(echo -n & | base64)"/g
    $s/$/\nEOF/
    p
  ' | sh | tr -d '[:space:]'
}

json_to_sh() {
  sed -rn '
    s/,/;/g
    s/\[/begin_json_array;/g; s/\]/end_json_array;/g
    s/\{/begin_json_object;/g; s/\}/end_json_object;/g
    s/("[^"]+"):/json_set_key \1;/g
    s/;("[^"]+")/;json_set string \1;/g
    s/;([0-9.]+)/;json_set number `echo -n \1 | base64`;/g
    s/;;/;/g
    s/;/\n/g
    p
  '
}

begin_json_object() {
  push_key %%%MAKEJSONOBJ%%%
}
end_json_object() {
  #echo end_json_object: $json_key >&2
  pop_key # TODO check if is %%%MAKEJSONOBJ%%%
  #echo obj: $1 `set | sed -rn "s/^(${json_key}_[a-zA-Z]+)_VALUE=(.*)/\1/p"` >&2
  #json_set object "`set | sed -rn "s/^(${json_key}_[a-zA-Z]+)_VALUE=(.*)/\1/p"`"
  json_set object "`set | sed -rn "s/^(${json_key}_[a-zA-Z]+)=(.*)/\1/p"`"
}
begin_json_array() { :; }
end_json_array() { :; }
json_push_key() {
  push_key "`echo -n "$1" | base64 -d`"
}
json_set_key() {
  pop_key
  json_push_key "$1"
}
json_set() {
  ##echo "typeof_$json_key=$1" >&2
  ##echo "${json_key}_VALUE=\"$2\"" >&2 # (`echo -n $2 | base64 -d`)" >&2
  #eval "${json_key}_TYPE=$1"
  #eval "${json_key}_VALUE=\"$2\""
  eval "typeof_${json_key}=$1"
  eval "${json_key}=\"$2\""
}

push_key() {
  json_key="${json_key+${json_key}_}$1"
}
pop_key() {
  json_key="`echo $json_key | sed 's/_[^_]\+$//'`"
}

json() {
  #eval echo "\"\$`echo -n "$json_key" "$@" | tr "$IFS" _`\" | base64 -d"
  NAME="`echo -n "$json_key" "$@" | tr "$IFS" _`"
  #eval "TYPE=\"\$${NAME}_TYPE\""
  eval "TYPE=\"\$typeof_$NAME\""

  echo -n "$TYPE $NAME: "
  case "$TYPE" in
    (object)
      #eval echo -n \$${NAME}_VALUE
      eval echo -n \$$NAME
      ;;
      #set | sed -rn "s/^(${NAME})_([a-zA-Z]+)[a-zA-Z_]*_VALUE=(.*)/\1_\2/p" |
      #    sort | uniq | tr \\n \ ;;
    (*) #echo -n "$VALUE";;
      #eval "VALUE=\"\$(echo -n \"\$${NAME}_VALUE\" | base64 -d)\""
      #eval echo -n \"\$${NAME}_VALUE\" | base64 -d
      eval echo -n \$${NAME} | base64 -d
  esac
  echo
}

read_json() {
  json_key="${1-JSON}"
  #meh="`cat`"
  #echo "$meh"
  ##echo "$meh" | normalize_json | json_to_sh; exit
  #eval "`echo "$meh" | normalize_json | json_to_sh`"
  eval "`normalize_json | json_to_sh`"
}

# TODO print_json x, print_json x ca ... to print as json

read_json x
echo ====
set | egrep "^(typeof_)?$json_key[A-Za-z_]*="
echo ====
json
json a
json b
json c
json c ca
json c cb
json d
#echo ====
#echo $JSON_VALUE
#echo $JSON_c_cb_VALUE | base64 -d; echo

echo READY.
#### End of file.
