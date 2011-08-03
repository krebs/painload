#INITD = /etc/init.d/
INITD = /etc/rc.d/
streams = groove deepmix radiotux
CURRDIR = ${PWD}
.PHONY: all
.PHONY: $(streams)

all: $(streams)
	@update-rc.d groove defaults 2>/dev/null || echo "[31;1m**[31;1;5m put groove daemon in DAEMONS in /etc/rc.conf[m"


$(streams):
	ln -n -s -f $$PWD/stream-starter $(INITD)$@
