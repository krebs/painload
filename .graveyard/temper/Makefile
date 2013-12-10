
all: infest
infest: temper rules-install
CFLAGS = -O2 -Wall -DDEBUG

temper:	temper.c 
	${CC} -DUNIT_TEST -o $@ $^ -lusb
	chmod +s temper
	#cp -a temper /usr/bin
clean:		
	rm -f temper *.o

rules-install: /etc/udev/rules.d/99-tempsensor.rules
/etc/udev/rules.d/99-tempsensor.rules:
	cp 99-tempsensor.rules /etc/udev/rules.d
debian-prereq:
	apt-get install libusb-dev
uninstall:
	rm -f /etc/udev/rules.d/99-tempsensor.rules /usr/bin/temper

