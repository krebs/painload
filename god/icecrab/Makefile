.phony: debian

debian:
	[ -e /usr/bin/icecast2 ] || apt-get install --yes icecast2
	cp icecast2 /etc/default/icecast2
	cp icecast.xml /etc/icecast2/icecast.xml
