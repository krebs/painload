
hooks := pre-commit
binaries := $(shell ls bin/)
.PHONY: all

all: $(addprefix ../db/.git/hooks/,$(hooks)) $(addprefix ../bin/,$(binaries))

../bin/%: bin/%
	cp $< $@
../db/.git/hooks/%: hooks/%
	cp $< $@
