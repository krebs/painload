
install: ../bin/punani
	
../bin/punani:
	ln -snvf ../punani/bin/punani ../bin/punani
debian:
	useradd punani||:
	cp autostart/punani-debian /etc/init.d/punani
	update-rc.d punani defaults
