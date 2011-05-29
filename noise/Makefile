
.PHONY: all
all: select-target

.PHONY: infest
infest:
	apt-get install --yes expect beep alsa-utils ucspi-tcp espeak
	f=/usr/bin/beep; chown krebs:krebs $$f && chmod 4755 $$f
	getent passwd noise || useradd noise
	ln -vsnf /krebs/noise/init.d/noise /etc/init.d/noise
	## tv: TODO update-rc.d is DEBIAN ONLY, fix this
	update-rc.d -f noise defaults
	amixer sset 'Master' 100 unmute || true
	amixer sset 'PCM' 100 unmute || true
	amixer sset 'PC Speaker' 100 unmute || \
	amixer sset 'Beep' 100 unmute || true
