.PHONY: update all install hosts

EXES := update_tinc_hosts fillxx update-retiolum-hosts

all: update links 

links:
	for x in $(EXES); do ln -vsnf ../retiolum/bin/$$x ../bin; done


install: upgrade
	../punani/bin/punani install tinc python
	scripts/tinc_setup/install.sh
	sudo cp scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up
	scripts/autostart/create-startup.sh

upgrade: update
	if ! diff -u scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up; then \
		sudo cp scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up; \
		sudo bin/restart-tincd || :; \
	fi

update: hosts
	bin/update_tinc_hosts "create magic" || :;
	bin/update_tinc_hosts restart
	sudo pkill -HUP tincd || :; 

hosts:
	bin/update-retiolum-hosts || :;
