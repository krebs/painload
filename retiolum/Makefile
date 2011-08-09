.phony: update it all so install

all: 
	cat Makefile

it: so
so: it

/etc/tinc/retiolum/hosts:
	cd $(dir $@) && git clone https://github.com/krebscode/hosts

#TODO conflicting 
update: /etc/tinc/retiolum/hosts
	cd $< && git pull

install: 
	scripts/tinc_setup/install.sh

autohosts: 
	@echo creating Magic
	bin/update_tinc_hosts "create magic" || true
	@echo adding hosts
	bin/update_tinc_hosts restart

arch-install: update install arch-autostart autohosts

arch-autostart:
	make -C scripts/autostart arch
