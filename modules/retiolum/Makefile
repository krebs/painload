.phony: update it all so install

all: select-target

it: so
so: it

/etc/tinc/retiolum/hosts:
	cd $(dir $@) && git clone https://github.com/krebscode/hosts

update: /etc/tinc/retiolum/hosts
	cd $< && git pull

install:
	curl -k https://github.com/miefda/retiolum/raw/master/.scripts/tinc_setup/bootstrap.sh | sh
