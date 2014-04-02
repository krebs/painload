#!/bin/sh
ip addr | grep ether | awk '{print $2}' | sort |md5sum | awk '{print $1}' | dd bs=1 count=6 2>/dev/null
