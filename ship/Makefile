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
