INITD = $(shell test -e /etc/rc.d/ && echo /etc/rc.d/ || echo /etc/init.d/)
streams = $(shell cut -d\  -f2 stream.db)
CURRDIR = ${PWD}
.PHONY: all $(streams)

all: $(streams)
	@update-rc.d groove defaults 2>/dev/null || echo "[31;1m**[31;1;5m put groove daemon in DAEMONS in /etc/rc.conf[m"

$(streams):
	@test -L $(INITD)$@ || test ! -e $(INITD)$@ && \
	ln -n -s -f $$PWD/stream-starter $(INITD)$@ && echo "writing $@ to $(INITD)"
	ln -sf $$PWD/streams ../bin/streams
