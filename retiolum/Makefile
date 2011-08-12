.PHONY: update all install hosts

EXES := update_tinc_hosts fillxx update-retiolum-hosts

all: update links 

links:
	for x in $(EXES); do ln -vsnf ../retiolum/bin/$$x ../bin; done

hosts:
	bin/update-retiolum-hosts

install: update
	@# will not run automatically
	scripts/tinc_setup/install.sh
	scripts/autostart/create-startup.sh

update: hosts
	@echo creating Magic
	bin/update_tinc_hosts "create magic" || true
	@echo adding hosts
	bin/update_tinc_hosts restart

arch-install: update install arch-autostart autohosts

arch-autostart:
	make -C scripts/autostart arch
