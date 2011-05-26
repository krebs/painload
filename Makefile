

.PHONY: all
all: select-target

.PHONY: aggressive
.PHONY: coop
.PHONY: infest
infest: aggressive
aggressive: 
	infest/etc_aggressive
	infest/home
coop: 
	infest/etc_coop
	infest/home

install-debian:
	[ `which git` ] || apt-get install git-core
	[ `which tmux` ] || apt-get install tmux
	[ `which screen` ] && apt-get remote screen
	[ `which vim` ] || apt-get install vim

noise:
	make -C modules/noise infest

