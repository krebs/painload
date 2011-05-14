

.PHONY: all
all: select-target

.PHONY: infest
infest:
	infest/etc
	infest/root
	make -C modules/noise infest
