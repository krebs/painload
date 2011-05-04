

.PHONY: all
all: select-target

.PHONY: infest
infest:
	infest/passwd
	infest/motd
