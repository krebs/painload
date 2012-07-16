.PHONY: all install
all: select-target

exes := $(shell \
	find . -mindepth 1 -maxdepth 1 -type f -executable -exec basename \{\} \;)

target_exes := $(addprefix ../../bin/,$(exes))

install: $(target_exes)

../../bin/%: % SOAPpy
		ln -snf ../ovh/soapi/$* $@

src:
	mkdir $@

src/SOAPpy: src
	cd $< && \
		svn co https://pywebsvcs.svn.sourceforge.net/svnroot/pywebsvcs/trunk/SOAPpy

src/SOAPpy/build/lib/SOAPpy: src/SOAPpy
	cd $< && python setup.py build

SOAPpy: src/SOAPpy/build/lib.linux-x86_64-2.6/SOAPpy
	ln -snf $<
