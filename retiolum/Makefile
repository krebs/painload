RETIOLUM_HOSTS = /etc/tinc/retiolum/hosts

.PHONY: update it all so install

all: update links 

links: 
	ln -sf $$PWD/bin/update_tinc_hosts ../bin/update_tinc_hosts
	ln -sf $$PWD/bin/fillxx ../bin/fillxx

it: so
so: it

hosts/:
	@echo "Writing new copy of hosts"
	[ -e $(RETIOLUM_HOSTS) ] || mkdir -p $(RETIOLUM_HOSTS)
	cp -r hosts/* $(RETIOLUM_HOSTS)/


install: autohosts
	@# will not run automatically
	scripts/tinc_setup/install.sh

update: hosts/
	@echo creating Magic
	bin/update_tinc_hosts "create magic" || true
	@echo adding hosts
	bin/update_tinc_hosts restart

arch-install: update install arch-autostart autohosts

arch-autostart:
	make -C scripts/autostart arch
