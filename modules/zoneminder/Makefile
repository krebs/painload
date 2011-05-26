
.PHONY: fix it so hard
it: so
so: it hard fix
	apt-get install --yes zoneminder libv4l-0

hard: /etc/sysctl.d/zoneminder.conf
/etc/sysctl.d/zoneminder.conf: zoneminder.conf
	cp $< $@
	sysctl -p $@

fix: zmdc.pl-LD_PRELOAD.patch
	(cd /usr/bin && patch -N) < $< || :

