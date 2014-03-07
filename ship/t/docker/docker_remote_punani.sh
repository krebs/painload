#!/bin/sh
cd $(dirname $(readlink -f $0))
docker_id=$(docker run -rm=true -d -v $PWD/punani/:/test  ubuntu /bin/sh /test/remote_punani)
trap "docker rm $docker_id" INT TERM EXIT QUIT
docker wait $docker_id
