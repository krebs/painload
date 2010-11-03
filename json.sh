#! /bin/sh
set -euf

# TODO check json first

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
    s/;("[^"]+")/;json_set STR \1;/g
    s/;([0-9]+)/;json_set INT `echo -n \1 | base64`;/g
    s/;;/;/g
    s/;/\n/g
    p
  '
}

begin_json_object() {
  push_key %%%MAKEJSONOBJ%%%
}
end_json_object() {
  #echo end_json_object: $key >&2
  #echo `echo "$key_stack" | head -n 1` >&2
  pop_key # TODO check if is %%%MAKEJSONOBJ%%%
  set -- `print_key`
  #echo object: $1 >&2; set | sed -rn "s/^($1_[a-zA-Z]+)_VALUE=(.*)/\1/p" >&2
  json_set OBJ "`set | sed -rn "s/^($1_[a-zA-Z]+)_VALUE=(.*)/\1/p"`"
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
  ##echo "`print_key`$1=$2 (`echo -n $2 | base64 -d`)" >&2
  #echo "`print_key`TYPE=$1" >&2
  #echo "`print_key`VALUE=\"$2\"" >&2 # (`echo -n $2 | base64 -d`)" >&2
  eval "`print_key`_TYPE=$1"
  eval "`print_key`_VALUE=\"$2\""
}

push_key() {
  key="${key+${key}_}$1"
  #key_stack="$1
#$key_stack"
}
pop_key() {
  key="`echo $key | sed 's/_[^_]\+$//'`"
  #key_stack="`echo "$key_stack" | sed 1d`"
}
print_key() {
  ##echo \<`echo print_key: $key`, `echo "$key_stack" | tac | tr '\n' _`\> >&2
  #echo "$key_stack" | tac | tr '\n' _
  echo -n "$key"
}

json() {
  #eval echo "\"\$`echo -n JSON "$@" | tr "$IFS" _`\" | base64 -d"
  NAME="`echo -n JSON "$@" | tr "$IFS" _`"
  eval "TYPE=\"\$${NAME}_TYPE\""

  echo -n "$TYPE $NAME: "
  case "$TYPE" in
    (OBJ)
      eval echo -n \$${NAME}_VALUE
      ;;
      #set | sed -rn "s/^(${NAME})_([a-zA-Z]+)[a-zA-Z_]*_VALUE=(.*)/\1_\2/p" |
      #    sort | uniq | tr \\n \ ;;
    (*) #echo -n "$VALUE";;
      #eval "VALUE=\"\$(echo -n \"\$${NAME}_VALUE\" | base64 -d)\""
      eval echo -n \"\$${NAME}_VALUE\" | base64 -d
  esac
  echo
}

key='JSON'
#key_stack='JSON'
meh="`cat`"
echo "$meh"
#echo "$meh" | normalize_json | json_to_sh; exit
eval "`echo "$meh" | normalize_json | json_to_sh`"
#echo ====
#set | grep '^JSON[A-Za-z_]*='
#echo ====
json
json a
json b
json c
json c ca
json c cb

echo READY.
#### End of file.
