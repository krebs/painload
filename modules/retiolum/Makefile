.phony: update install all

all: select-target

update:
	git pull /etc/tinc/retiolum/hosts
install:
	curl -k https://github.com/miefda/retiolum/raw/master/.scripts/tinc_setup/bootstrap.sh | sh
