install: /etc/lcd4linux.conf
	#punani -Ei libtool automake autoconf zlib1g-dev libssl-dev python-dev libc6 libusb-dev libibus-dev subversion libgd2-noxpm-dev libgd2-noxpm
	dpfhack_display/build-dpf-lcd4linux.sh
	make -C dpfhack_display/lcd4linux/ install

/etc/lcd4linux.conf: lcd4linux.conf
	chown 0:0 lcd4linux.conf
	cp -a lcd4linux.conf /etc/lcd4linux.conf
