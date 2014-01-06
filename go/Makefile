help:;@grep -v ^help: Makefile

install: \
		/etc/systemd/system/go.service \
		/etc/conf.d/go.env
	systemctl daemon-reload

/etc/%: etc/%
	@! test -e $@ || { echo file already exists: $@; exit 23; }
	mkdir -p $(dir $@)
	cp $< $@
