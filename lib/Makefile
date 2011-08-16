

.PHONY: all install
all: select-target

install: ../bin/libkrebs.sh

../bin/libkrebs.sh: libkrebs.sh
	ln -vsnf ../lib/$< $@
