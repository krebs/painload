NAGDIR = /etc/nagios3/
NAGLIBDIR = /usr/lib/nagios
HTDOCS = /usr/share/nagios3/htdocs

.phony: debian
debian:
	[ `which nagios3` ] || apt-get install nagios3
	rm $(NAGDIR)/conf.d/* || true
	cp -r conf/* $(NAGDIR)/conf.d/
	htpasswd -bc htpasswd.users nagiosadmin krebs
	htpasswd -b htpasswd.users shack shackit
	sed -i 's/\(authorized_for_all_hosts=nagiosadmin\)$$/\1,shack/' $(NAGDIR)/cgi.cfg
	sed -i 's/\(authorized_for_all_services=nagiosadmin\)$$/\1,shack/' $(NAGDIR)/cgi.cfg
	cp -R htdocs/* $(HTDOCS)
	cp -r plugins $(NAGLIBDIR)
	/etc/init.d/nagios3 reload
