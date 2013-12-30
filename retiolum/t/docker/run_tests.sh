#!/bin/sh

docker run -v $PWD/docker_tests/:/test  ubuntu /test/bootstrap
