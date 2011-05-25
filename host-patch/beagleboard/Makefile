.PHONY: all
all: select-target

patchfile:
	diff /krebs/etc/profile /etc/profile > profile.patch || true

patch:
	cd /;\
		patch -p0 < /krebs/host-patch/beagleboard/profile.patch
