DISTVERSION = 0.12devel

CURDIR = $(shell pwd)

# Make sure this path is correct. Needs to point to dpf.h and libdpf.a
DPFLIB = dpflib
PYDPF = python

FILES = Makefile lcd4linux-svn1142-dpf.patch README Changelog

ifndef DESTDIR
DESTDIR = /tmp
endif

default: $(DPFLIB)/libdpf.a
	-[ -e src ] && (cd src; ./buildall.sh)
	$(MAKE) -C $(PYDPF) install

all: default lcd4linux/lcd4linux

$(DPFLIB)/libdpf.a:
	$(MAKE) -C $(DPFLIB) install

lcd4linux/lcd4linux: $(DPFLIB)/libdpf.a
	./build-dpf-lcd4linux.sh $(CURDIR)

dist: installdist
	tar cfz /tmp/dpfhack-$(DISTVERSION).tgz --numeric-owner -C $(DESTDIR) dpf


PYSCRIPTS += detect.py fulldump.py profiles.py hackit.py
PYSCRIPTS += chartbl.py update.py

LIBFILES += Makefile dpflib.c fwload.c rawusb.c
LIBFILES += sglib.h dpf.h 

FILES += fw/README unixdll.mk
FILES += $(PYDPF)/Makefile $(PYDPF)/py_device.c
FILES += include/usbuser.h include/flash.h
FILES += $(LIBFILES:%=$(DPFLIB)/%)
FILES += $(wildcard src/p_*.s) $(wildcard src/jmptbl*.s)

FILES += reverse/common.in reverse/dump.py reverse/Makefile reverse/README

DPFINST = $(DESTDIR)/dpf

installdist:
	install -d $(DPFINST)
	install -d $(DPFINST)/include
	install -d $(DPFINST)/reverse
	install -d $(DPFINST)/src
	install -d $(DPFINST)/fw
	install -d $(DPFINST)/dpflib
	install -d $(DPFINST)/python
	install -d $(DPFINST)/fw/hexfiles
	install -m644 include/flash.h $(DPFINST)/include
	cp -r fw/hexfiles $(DPFINST)/fw
	install -m644 fw/font4x8.bin $(DPFINST)/fw
	install -m755 $(PYSCRIPTS:%=fw/%) $(DPFINST)/fw
	install -m755 build-dpf-lcd4linux.sh $(DPFINST)
	for i in $(FILES); do \
		install -m644 $$i $(DPFINST)/$$i; \
	done
	install -m600 dpf.conf $(DPFINST)
	install -m600 dpfbig.conf $(DPFINST)
	cd $(DPFINST)/fw; ln -sf ../Debug .

clean:
	rm -fr $(DPFINST)
	$(MAKE) -C $(DPFLIB) clean
	$(MAKE) -C $(PYDPF) clean
	-[ -e lcd4linux/Makefile ] && (cd lcd4linux; make distclean)
