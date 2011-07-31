DIST = debian

.PHONY: infest all
all: select-target

infest:
	make -C infest

install-core:
	core/$(DIST)

noise:
	make -C noise infest
streams:
	make -C streams
monitoring:
	make -C Monitoring debian
zoneminder:
	make -C zoneminder fix it so hard
