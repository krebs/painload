INIT_FOLDER=/etc/init.d
.phony: all
all:
	#TODO change the tinc file before writing
	cp tinc $(INIT_FOLDER)/tinc
	chmod +x $(INIT_FOLDER)/tinc
	echo "retiolum" > /etc/tinc/nets.boot
	update-rc.d tinc defaults
