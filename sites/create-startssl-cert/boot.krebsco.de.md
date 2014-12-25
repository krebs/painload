# generate key

    $ openssl genrsa -out ~/boot.krebsco.de.key 2048
    $ openssl req -new -sha256 -key ~/boot.krebsco.de.key -out ~/boot.krebsco.de.csr
    Country Name (2 letter code) [AU]:XX
    State or Province Name (full name) [Some-State]:
    Locality Name (eg, city) []:
    Organization Name (eg, company) [Internet Widgits Pty Ltd]:Krebsco  
    Organizational Unit Name (eg, section) []:
    Common Name (e.g. server FQDN or YOUR name) []:boot.krebsco.de
    Email Address []:root@krebsco.de

    Please enter the following 'extra' attributes
    to be sent with your certificate request
    A challenge password []:
    An optional company name []:

    # everything besides public key will be ignored so do not bother
    $ firefox https://www.startssl.com/
