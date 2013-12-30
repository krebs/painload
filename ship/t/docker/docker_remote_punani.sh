#!/bin/sh
cd $(dirname $(readlink -f $0))
docker run -v $PWD/punani/:/test  ubuntu /bin/sh /test/remote_punani >/dev/null
