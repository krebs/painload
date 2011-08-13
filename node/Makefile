
ifndef version
	version := $(shell \
		curl -sS http://nodejs.org/ | \
			../util/bin/hrefs | \
			sed -rn 's:.*node-(v[0-9.]+)\.tar\.gz:\1:p' | \
			sort | \
			tail -n 1)
endif

export CPPFLAGS := -Wno-unused-but-set-variable

.PHONY: all build install

all:
	@echo "You are made of stupid!"; exit 23

build: out/node-$(version)

install: out/node-$(version)
	ln -vsnf ../node/$</bin/node ../bin/node

out/node-%: src/node-%
	cd $< && ./configure --prefix=$(PWD)/$@
	make -C $<
	make -C $< install

../bin/node: out/

src/node-git: src
	cd src && \
		git clone https://github.com/joyent/node node-git

src/node-%: src/node-%.tar.gz
	cd src && tar xf node-$*.tar.gz

.PRECIOUS: src/node-%.tar.gz
src/node-%.tar.gz: /usr/bin/curl src
	{ curl -o $@ http://nodejs.org/dist/node-$*.tar.gz && gzip -t $@; } || \
		{ curl -o $@ http://nodejs.org/dist/$*/node-$*.tar.gz && gzip -t $@; }

/usr/bin/curl:
	apt-get install --yes curl

src:
	mkdir -v -p $@
