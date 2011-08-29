build-deps:
	#punani -Ei libtool automake autoconf zlib1g-dev libssl-dev python-dev libc6 libusb-dev libibus-dev subversion libgd2-noxpm-dev libgd2-noxpm lcd4linux

/usr/bin/lcd4linux: build-deps
	#punani -Ei lcd4linux
	sed -i 's/usr\/sbin\/lcd4linux/usr\/bin\/lcd4linux/g' /etc/init.d/lcd4linux 
	dpfhack_display/build-dpf-lcd4linux.sh
	make -C dpfhack_display/lcd4linux/ install

lcd4linux_autostart:
	# service lcd4linux start
	# update-rc.d lcd4linux

install:  /usr/bin/lcd4linux /etc/lcd4linux.conf lcd4linux_autostart
	# TODO this is debian only

update: /etc/lcd4linux.conf
	service lcd4linux force-reload

/etc/lcd4linux.conf: lcd4linux.conf
	chown krebs:krebs lcd4linux.conf
	chmod 600 lcd4linux.conf
	cp -a lcd4linux.conf /etc/lcd4linux.conf
