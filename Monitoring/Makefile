NAGDIR = /etc/nagios3/
NAGLIBDIR = /usr/lib/nagios
HTDOCS = /usr/share/nagios3/htdocs

.phony: debian
debian:
	[ `which python` ] || apt-get install python python-simplejson
	[ `which nagios3` ] || apt-get install nagios3
	rm $(NAGDIR)/conf.d/* || true
	cp -r conf/* $(NAGDIR)/conf.d/
	htpasswd -bc htpasswd.users nagiosadmin krebs
	htpasswd -b htpasswd.users shack shackit
	sed -i 's/\(authorized_for_all_hosts=nagiosadmin\)$$/\1,shack/' $(NAGDIR)/cgi.cfg
	sed -i 's/\(check_external_commands=\)0$$/\11/' $(NAGDIR)/nagios.cfg
	sed -i 's/\(authorized_for_all_services=nagiosadmin\)$$/\1,shack/' $(NAGDIR)/cgi.cfg
	cp -R htdocs/* $(HTDOCS)
	cp -r plugins $(NAGLIBDIR)
	/etc/init.d/nagios3 reload
	chown nagios:www-data /var/lib/nagios3 || true
	chown nagios:www-data /var/lib/nagios3/rw || true
	chmod g+x /var/lib/nagios3 || true
	chmod ug=rwx /var/lib/nagios3/rw/nagios.cmd || true
