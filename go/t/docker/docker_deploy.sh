#!/bin/bash
cd $(dirname $(readlink -f $0))
rnd_port=$(shuf -i 2000-65000 -n 1)
docker_id=$(docker run -p $rnd_port:80 -d -v  /krebs/go/t/docker/../../../:/krebs ubuntu /bin/bash /krebs/go/t/docker/dockertest/deploy)
#docker run -p $rnd_port:80  -v  /krebs/go/t/docker/../../../:/krebs ubuntu /bin/bash /krebs/go/t/docker/dockertest/deploy
echo $docker_id on $rnd_port
docker stop $docker_id
