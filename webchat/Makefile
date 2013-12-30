server.key:
	openssl genrsa -des3 -out server.key 2048
server_npw.key: server.key
	openssl rsa -in server.key -out server_npw.key
server.csr: server_npw.key
	openssl req -new -key server_npw.key -out server.csr
server.crt: server.csr server_npw.ley
	openssl x509 -req -days 365 -in server.csr -signkey server_npw.key -out server.crt
