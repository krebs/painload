.phony: debian
debian:
	[ `which nagios3` ] || apt-get install nagios
	cp -r conf/* /etc/nagios3/conf.d/
	cp -R htdocs/* /usr/share/nagios3/htdocs/
	cp -r plugins /usr/lib/nagios
	/etc/init.d/nagios3 reload
