

.PHONY: all
all: select-target

.PHONY: infest
infest:
	infest/etc
	make -C modules/noise infest
