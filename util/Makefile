usage:;cat Makefile

test: export PATH := "$(PWD)/bin:$(PATH)"
test:
	@tests="`find t -type f -executable`"; \
		i=1; \
		echo $$i..`echo "$$tests" | wc -l`; \
		for t in $$tests; do \
			./$$t; \
			case $$? in 0) ok=ok;; *) ok='not ok';; esac; \
			echo $$ok $$i - $$t; \
			(( i++ )); \
		done
