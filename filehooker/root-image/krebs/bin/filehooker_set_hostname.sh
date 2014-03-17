#!/usr/bin/bash
hostn="filehooker$RANDOM"
echo "$hostn" > /etc/hostname
hostname $hostn

