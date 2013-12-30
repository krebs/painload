.PHONY: update all install hosts

EXES := update_tinc_hosts fillxx update-retiolum-hosts

all: update links 

links:
	for x in $(EXES); do ln -snf ../retiolum/bin/$$x ../bin; done


install: upgrade
	sudo cp scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up

upgrade: update
	if ! sudo diff -u scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up; then \
		sudo cp scripts/tinc_setup/tinc-up /etc/tinc/retiolum/tinc-up; \
		sudo pkill -HUP tincd || :; \
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

test:
	@export PATH="$(CURDIR)/bin:$(PATH)"; \
		tests="`find t -type f -executable`"; \
		i=1; \
		pids="";\
		n=`echo "$$tests" | wc -l`; \
		echo $$i..$$n; \
		for exe in $$tests; do \
			{ \
				./$$exe; \
				ret=$$?; \
				case $$ret in 0) result=ok;; *) result='not ok';; esac; \
				echo $$result $$i - $$exe; \
				exit $$ret;\
			} & \
			pids="$${pids} $$!" \
			i=$$(( i+1 )); \
		done; \
		ret=0;\
		for pid in $$pids; do \
			wait $$pid || ret=23;\
		done; \
		exit $$ret;
