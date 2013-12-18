# Makefile for the rcontrol program
# We set a setuid bit as this tools needs root privilleges to open the FT232 device.

BINARY=./rcontrol

install: all
	ln -snf $$PWD/$(BINARY) ../../bin/

all:$(BINARY)
	chown root.root $(BINARY)
	chmod +s $(BINARY)

$(BINARY): rcontrol.c
	#punani install libftdi1 libftdi-dev
	gcc -Wall -lusb -lftdi rcontrol.c -o $(BINARY)

clean:
	rm -f $(BINARY)
