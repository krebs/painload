DIST = debian

.PHONY: all
all: select-target

.PHONY: infest aggressive coop 

infest: aggressive
aggressive: 
	infest/etc_aggressive
	infest/home
coop: 
	infest/etc_coop
	infest/home

install-core:
	core/$(DIST)

noise:
	make -C modules/noise infest
streams:
	make -C modules/streams
monitoring:
	make -C modules/Monitoring debian
zoneminder:
	make -C modules/zoneminder fix it so hard
