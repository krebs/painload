all:	temper

CFLAGS = -O2 -Wall

temper:	temper.c
	${CC} -DUNIT_TEST -o $@ $^ -lusb

clean:		
	rm -f temper *.o

rules-install:			# must be superuser to do this
	cp 99-tempsensor.rules /etc/udev/rules.d
