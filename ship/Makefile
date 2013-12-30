exesrcdir := src
libsrcdir := lib
tmpoutdir := tmp
finoutdir := ../bin

exesrcs := $(notdir $(wildcard $(exesrcdir)/*))
exetmpouts := $(addprefix $(tmpoutdir)/,$(exesrcs))
exefinouts := $(addprefix $(finoutdir)/,$(exesrcs))

build := BUILD_PATH=$(libsrcdir) ./build

.PHONY: all install clean distclean

all: $(exetmpouts)

install: $(exefinouts)

clean:
	rm -f $(exetmpouts)

distclean: clean
	rm -f $(exefinouts)

define buildrule
$(tmpoutdir)/$(1): $(exesrcdir)/$(1) $(shell $(build) deps $(exesrcdir)/$(1))
	$(build) compile $$< $$@
endef

$(foreach exe, $(exesrcs), $(eval $(call buildrule,$(exe))))

$(finoutdir)/%: $(tmpoutdir)/%
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
