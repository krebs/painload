.PHONY: update all install hosts

EXES := update_tinc_hosts fillxx update-retiolum-hosts

all: update links 

links:
	for x in $(EXES); do ln -snf ../retiolum/bin/$$x ../bin; done


install: upgrade
	sudo cp scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up

upgrade: update
	if ! diff -u scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up; then \
		sudo cp scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up; \
		sudo pkill -HUP tincd || :; 
	fi

update: hosts
	bin/update_tinc_hosts "create magic" || :;
	bin/update_tinc_hosts restart
	sudo pkill -HUP tincd || :; 

startup:
	scripts/autostart/create-startup.sh

hosts:
	bin/update-retiolum-hosts || :;
	sudo bin/patch-retiolum-hosts
