all: node_modules GeoLiteCity.dat

node_modules: package.json
	npm install
	@touch -r $< $@

GeoLiteCity.dat:
	@test -e GeoLiteCity.dat && ln -s GeoLiteCity.dat $@ || { \
		echo 'No GeoIP City database found.'; \
		echo 'You can get one from http://dev.maxmind.com/geoip/geolite:'; \
		echo '  wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'; \
		echo '  gunzip GeoLiteCity.dat.gz'; \
		exit 23; \
	}

