
CC := gcc -std=c99
CFLAGS := -D_XOPEN_SOURCE=500
LIBS := $(shell pkg-config --cflags --libs jack)

.PHONY: all clean

all: a.out

clean:
	rm -f a.out

a.out: index.c
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)
