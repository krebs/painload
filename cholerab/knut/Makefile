

.PHONY: all install

all:
	echo 'Error 1: You are made of stupid!' >&2
	exit 23

install: \
	../../bin/cnot \
	../../bin/clive-knut \
	../../bin/ttycnser-login
	../../punani/bin/punani -Ei python python-notify dbus-python

../../bin/cnot: clients/cnot/index
	ln -vsnf ../cholerab/knut/$< $@

../../bin/clive-knut: index.js
	ln -vsnf ../cholerab/knut/$< $@

../../bin/ttycnser-login: plugs/ttycnser/bin/login
	ln -vsnf ../cholerab/knut/$< $@
