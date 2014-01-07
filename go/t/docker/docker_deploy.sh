#!/bin/bash
cd $(dirname $(readlink -f $0))
set -euf
rnd_port=$(shuf -i 2000-65000 -n 1)
docker_id=$(docker run -p $rnd_port:80 -d -v  /krebs/go/t/docker/../../../:/krebs ubuntu /bin/bash /krebs/go/t/docker/dockertest/deploy)
#docker run -p $rnd_port:80  -v  /krebs/go/t/docker/../../../:/krebs ubuntu /bin/bash /krebs/go/t/docker/dockertest/deploy
echo $docker_id on $rnd_port
trap "docker stop $docker_id;docker rm $docker_id" INT TERM EXIT QUIT
i=0
max_wait=20
echo "waiting for install (takes about 3 minutes)"
sleep 240
while ! curl -s localhost:$rnd_port >/dev/null;do
    i=$((i+1))
    test $i -gt $max_wait && echo "timeout for installation reached, bailing out" && exit 1
    echo "http port not yet reachable ($i of $max_wait). waiting"
    sleep 10
done
short_uri=$(curl -F "uri=aids.balls" localhost:$rnd_port)
curl $short_uri -v | grep location: | grep aids.balls
