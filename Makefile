DIST = debian

.PHONY: infest it all so aggressive coop 
all: select-target

it: so
so: it coop
aggressive: coop
	infest/etc_aggressive
coop: 
	infest/etc_coop
	infest/home

# compatibility
infest: aggressive

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
