submodules = gxfr dnsrecon bxfr whatweb
security_modules = subdomains revip whatweb

all: init all-mods

init: init-submodules $(submodules)
init-submodules: 
	cd ..;git submodule init; git submodule update
$(submodules):
	cd repos/$@ ; git checkout master;git pull

all-mods: $(addprefix public_commands/,$(security_modules))
public_commands/%:commands/%
	ln -s ../$< $@

debian-autostart:
	useradd reaktor ||:
	cp startup/init.d/reaktor-debian /etc/init.d/reaktor
	cp startup/conf.d/reaktor /etc/default/
	update-rc.d reaktor defaults
supervisor-autostart:
	useradd reaktor ||:
	cp startup/supervisor/Reaktor.conf /etc/supervisor/conf.d/
