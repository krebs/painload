help:;@cat Makefile

export authorized_keys_file := authorized_keys
export services_file := services.txt
export host_key_file := test.key

test-client:
	ssh localhost -p 1337 2>/dev/null

test-server:
	python test.py

$(host_key_file):
	ssh-keygen -t rsa -P '' -f $@
