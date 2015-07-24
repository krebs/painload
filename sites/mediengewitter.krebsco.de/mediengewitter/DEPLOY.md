# docker

	docker build -t krebs/mediengewitter .
	# autostart this somehow
	docker run -p 127.0.0.1:8080:8080 -v /media/ext/magnet_pics/:/images krebs/mediengewitter

# nginx

	cp etc/nginx/sites-available/mediengewitter.krebsco.de.conf /etc/nginx/sites-available/
