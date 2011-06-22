

.PHONY: all build install

all:
	@echo "You are made of stupid!"; exit 23

build: node node/build/default/node
	cd node && ./configure && make

install: build
	cd node && make install

node: node-git
	ln -vsnf $< $@

node-git:
	git clone https://github.com/joyent/node node-git

node-%: /usr/bin/curl
	curl http://nodejs.org/dist/$@.tar.gz | tar zx

/usr/bin/curl:
	apt-get install --yes curl
