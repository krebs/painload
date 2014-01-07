help:;@grep -v ^help: Makefile

install: \
		/etc/systemd/system/go.service \
		/etc/conf.d/go.env
	systemctl daemon-reload

/etc/%: etc/%
	@! test -e $@ || { echo file already exists: $@; exit 23; }
	mkdir -p $(dir $@)
	cp $< $@

test:
	@export PATH="$(CURDIR)/bin:$(PATH)"; \
		tests="`find t -type f -executable`"; \
		i=1; \
		pids="";\
		n=`echo "$$tests" | wc -l`; \
		echo $$i..$$n; \
		for exe in $$tests; do \
			{ \
				./$$exe; \
				ret=$$?; \
				case $$ret in 0) result=ok;; *) result='not ok';; esac; \
				echo $$result $$i - $$exe; \
				exit $$ret;\
			} & \
			pids="$${pids} $$!" \
			i=$$(( i+1 )); \
		done; \
		ret=0;\
		for pid in $$pids; do \
			wait $$pid || ret=23;\
		done; \
		exit $$ret;
