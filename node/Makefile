

.PHONY: all
all: node-v0.4.8
	cd $< && ./configure && make && make install

node-%:
	cur http://nodejs.org/dist/$@.tar.gz | tar zx
