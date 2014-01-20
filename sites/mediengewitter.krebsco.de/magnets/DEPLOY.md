# docker

/media/ext/magnet_pics is the path to a lot of disk space which will be shared by magnets and mediengewitter.

	docker build -t krebs/magnets .
	# autostart this somehow
	docker run -v /media/ext/magnet_pics/:/images krebs/magnets
