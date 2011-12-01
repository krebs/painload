
hooks := pre-commit

.PHONY: all

all: $(addprefix ../db/.git/hooks/,$(hooks))

../db/.git/hooks/%: hooks/%
	cp $< $@
