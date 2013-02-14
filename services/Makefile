help:;@cat Makefile
export authorized_keys_file := authorized_keys
export debug_log := true
export services_file := services.txt
export host_key_file := test.key
export services_home := /opt/services

.PHONY: authorized_keys


service-user:  $(services_home)/services.txt ssh_authorized_keys
	@echo 'also make sure that the user is created: make create-service-user'

create-service-user:
	mkdir -p $(services_home)
	rmdir $(services_home)
	useradd -m -r -l -f -1 -d $(services_home) services

ssh_authorized_keys: $(services_home)/.ssh/authorized_keys

$(services_home)/.ssh:
	mkdir  $@
	chown services:services $@

$(services_home)/.ssh/authorized_keys: $(services_home)/.ssh $(authorized_keys_file)
	cp $(authorized_keys_file) $(services_home)/.ssh/authorized_keys
	@echo "restricting authorized_keys..."
	@sed -i 's#^#command="/bin/cat $(services_home)/services.txt",no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty #' $(services_home)/.ssh/authorized_keys

$(services_home)/services.txt:
	@echo 'make sure to configure the services correctly in $(services_home)/services.txt'
	cp $(services_file) $(services_home)/services.txt

	
test-client:
	ssh localhost -p 1337 2>/dev/null

test-server:
	./test-server.py

$(host_key_file):
	ssh-keygen -t rsa -P '' -f $@
