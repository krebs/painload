INIT_FOLDER=/etc/init.d
.phony: all
debian:
	#TODO change the tinc file before writing
	cp tinc /etc/init.d/tinc
	chmod +x /etc/init.d
	echo "retiolum" > /etc/tinc/nets.boot
	update-rc.d tinc defaults
arch:
	@cp tinc /etc/rc.d
	@chmod +x /etc/rc.d/tinc
	@echo "add tinc to DAEMONS in /etc/rc.conf"


