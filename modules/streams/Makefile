INITD = /etc/init.d/
streams = groove deepmix radiotux
.PHONY: all
.PHONY: $(streams)

all: $(streams)
	update-rc.d groove defaults

$(streams):
	cp $@ $(INITD)$@
