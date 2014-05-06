usage:;cat Makefile

test:
	@export PATH="$(CURDIR)/bin:$(PATH)"; \
		tests="`find t -type f -executable`"; \
		i=1; \
		n=`echo "$$tests" | wc -l`; \
		echo $$i..$$n; \
		for exe in $$tests; do \
			if ./$$exe; then \
				echo ok $$i - $$exe; \
			else \
				echo not ok $$i - $$exe; \
				touch .test-not-ok; \
			fi & \
			i=$$(( i+1 )); \
		done; \
		wait; \
		if test -e .test-not-ok; then \
			rm .test-not-ok; \
			exit 23; \
		fi
