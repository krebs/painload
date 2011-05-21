

.PHONY: all
all: select-target

.PHONY: infest
infest:
	infest/etc
	infest/root
	make -C modules/noise infest
install-debian:
	[ `which git` ] || apt-get install git-core
	[ `which tmux` ] || apt-get install tmux
	[ `which screen` ] && apt-get remote screen
	[ `which vim` ] || apt-get install vim

