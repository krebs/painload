#!/bin/sh
cd $(dirname $(readlink -f $0))
docker_id=$(docker run -d -rm=true -v $PWD/docker_tests/:/test  ubuntu /bin/sh /test/bootstrap )
trap "docker rm $docker_id" INT TERM EXIT QUIT
docker wait $docker_id
