usage:;cat Makefile

test:
	@export PATH="$(CURDIR)/bin:$(PATH)"; \
		tests="`find t -type f -executable`"; \
		i=1; \
		n=`echo "$$tests" | wc -l`; \
		echo $$i..$$n; \
		for exe in $$tests; do \
			{ \
				./$$exe; \
				case $$? in \
					0) result=ok;; \
					*) result='not ok'; touch .test-not-ok;; \
				esac; \
				echo $$result $$i - $$exe; \
			} & \
			i=$$(( i+1 )); \
		done; \
		wait; \
		if test -e .test-not-ok; then \
			rm .test-not-ok; \
			exit 23; \
		fi
