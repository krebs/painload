.PHONY: update all install hosts

EXES := update_tinc_hosts fillxx update-retiolum-hosts

all: update links 

links:
	for x in $(EXES); do ln -vsnf ../retiolum/bin/$$x ../bin; done

hosts:
	bin/update-retiolum-hosts || true

install: update
	../punani/bin/punani -Eih tinc /usr/bin/python /usr/bin/python2
	scripts/tinc_setup/install.sh
	cp scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up
	scripts/autostart/create-startup.sh

update: hosts
	bin/update_tinc_hosts "create magic" || true
	bin/update_tinc_hosts restart
	if ! diff -u scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up; then \
		sudo cp scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up; \
		sudo bin/restart-tincd; \
	else \
		sudo pkill -HUP tincd || :; \
	fi

arch-install: update install arch-autostart autohosts

arch-autostart:
	make -C scripts/autostart arch || true
