INIT_FOLDER=/etc/rc.d
.phony: all
all:
	#TODO change the tinc file before writing
	cp tinc $(INIT_FOLDER)/tinc
	echo "retiolum" > /etc/tinc/nets.boot
	update-rc.d tinc defaults
