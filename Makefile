

.PHONY: all
all: select-target

.PHONY: infest
infest:
	infest/passwd
	infest/motd
	cat etc/profile >/etc/profile
