DIST = debian

.PHONY: infest all
all: select-target

infest:
	make -C modules/infest

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
