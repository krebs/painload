init:
	cd ..;git submodule init; git submodule update
	cd repos/gxfr/; git checkout master; git pull
	cd repos/dnsrecon; git checkout master; git pull
	cd repos/dnsmap; git checkout master; git pull



debian-autostart:
	useradd reaktor ||:
	cp autostart/reaktor-debian /etc/init.d/reaktor
	cp autostart/reaktor /etc/default/
	update-rc.d reaktor defaults
