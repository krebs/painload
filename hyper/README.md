# Overview

## start conductor on port 8888 and sink on 1337

    //hyper/process/main
    //bin/node //hyper/sink

## create bc process and retrieve it's process id (AKA {path})

    url=http://localhost:8888
    curl -fvsS --data-binary @//hyper/process/test/bc.json $url/proc

## send data for calculation

    echo 9000+2^42 | curl -fvsS --data-binary @- $url/{path}

## spawn process with http influx and local efflux

hint: maybe run each command in some separate terminal.

    id=dummy sh -x //hyper/process/spawn stdbuf -o 0 sed 's/[^0-9 ]//g'
    port=3 node //hyper/influx/http //proc/dummy/0
    cat //proc/dummy/1
    cat //proc/dummy/2
    date | curl -fvsS --data-binary @- http://localhost:3

## calculate the square of the current year in a little local hyper sewer system

hint: maybe run each command in some separate terminal.

    id=sqr sh -x //hyper/process/spawn stdbuf -o 0 sed 's/[^0-9]//g;s/.*/(&)^2/'
    id=bc sh -x //hyper/process/spawn bc
    port=42 node //hyper/influx/http //proc/sqr/0
    cat //proc/sqr/1 > //proc/bc/0
    cat //proc/bc/1
    date +%Y | curl -fvsS --data-binary @- http://localhost:42
