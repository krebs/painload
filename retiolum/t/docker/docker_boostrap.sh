#!/bin/sh
cd $(dirname $(readlink -f $0))
docker run -v $PWD/docker_tests/:/test  ubuntu /bin/sh /test/bootstrap >/dev/null
