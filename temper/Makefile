
all: infest
infest: temper
CFLAGS = -O2 -Wall

temper:	temper.c rules-install
	${CC} -DUNIT_TEST -o $@ $^ -lusb
	chmod +s temper
	cp -a temper /usr/bin
clean:		
	rm -f temper *.o
rules-install:			# must be superuser to do this
	cp 99-tempsensor.rules /etc/udev/rules.d
debian-prereq:
	apt-get install libusb-dev
uninstall:
	rm -f /etc/udev/rules.d/99-tempsensor.rules /usr/bin/temper

