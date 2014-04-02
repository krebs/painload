#!/bin/sh
hostn="elch_$(/krebs/bin/macid.sh)"
hostnamectl set-hostname "$hostn"
hostname $hostn
echo "$hostn" > /etc/hostname
