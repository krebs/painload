.PHONY: infest
BIN_DIR = ../bin
infest:
	ln -s ${PWD}ivan ${INSTALL_DIR}
debian-startup:
	cp ivan-startup /etc/init.d/ivan
	update-rc.d ivan start
