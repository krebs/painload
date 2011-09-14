# Overview

## start conductor on port 8888 and sink on 1337

    //hyper/process/main
    //bin/node //hyper/sink

## create bc process and retrieve it's process id (AKA {path})

    url=http://localhost:8888
    curl -fvsS --data-binary @//hyper/process/test/bc.json $url/proc

## send data for calculation

    echo 9000+2^42 | curl -fvsS --data-binary @- $url/{path}
