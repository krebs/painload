.PHONY: all format install configure
select-target:
	@echo "You are made of stupid!"
	echo "look here"
	@cat Makefile
format:
	cat README
install: configure
	apt-get install --yes lm-sensors
	echo '#!/bin/bash' > /usr/bin/ati_license
	echo '#!/bin/sh' > /etc/init.d/live-boot
	echo 'wall "going down"' >> /etc/init.d/live-boot
	chmod 755 /etc/init.d/live-boot
	echo 'sudo tar xvf /opt/AMD-APP-SDK-v2.4-lnx64/icd-registration.tgz -C /' >> /usr/bin/ati_license
	cp -r user /home
configure:
	sensors-detect
	@cat CONFIGURE
