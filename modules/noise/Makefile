
.PHONY: all
all: select-target

.PHONY: infest
infest:
	apt-get install --yes expect beep alsa-utils ucspi-tcp espeak
	f=/usr/bin/beep; chown krebs:krebs $$f && chmod 4755 $$f
	getent passwd noise || useradd noise
	ln -vsnf /krebs/modules/noise/init.d/noise /etc/init.d/noise
	update-rc.d -f noise defaults
	##
	amixer sset 'Master' 100 unmute
	amixer sset 'PCM' 100 unmute
	amixer sset 'PC Speaker' 100 unmute || \
	amixer sset 'Beep' 100 unmute
