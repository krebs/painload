.PHONY: all format install
select-target:
	@echo "You are made of stupid!"
format:
	cat README
install:
	echo '#!/bin/bash' > /usr/bin/ati_license
	echo 'sudo tar xvf /opt/AMD-APP-SDK-v2.4-lnx64/icd-registration.tgz -C /' >> /usr/bin/ati_license
	cp -r user /home
configure:
	cat CONFIGURE
