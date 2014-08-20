Dradis is installed on Kalle at port 3004 via ssl. Kalle is a Kali Linux instance:
 - http://dradisframework.org/install.html

pigstarter forwards ssl via nginx:


    # enable reverse proxy
    proxy_redirect              off;
    proxy_set_header            Host            $http_host;
    proxy_set_header            X-Real-IP       $remote_addr;
    proxy_set_header            X-Forwared-For  $proxy_add_x_forwarded_for;

    upstream streaming_example_com 
    {
          server kalle:3004; 
    }

    server 
    {
        listen      8443 default ssl;
        #server_name streaming.example.com;
        #access_log  /tmp/nginx_reverse_access.log;
        #error_log   /tmp/nginx_reverse_error.log;
        root        /usr/local/nginx/html;
        index       index.html;

        ssl_session_cache    shared:SSL:1m;
        ssl_session_timeout  10m;
        ssl_certificate /etc/nginx/ssl/pigstarter.crt;
        ssl_certificate_key /etc/nginx/ssl/pigstarter.key;
        ssl_verify_client off;
        proxy_ssl_session_reuse off;
        ssl_protocols        SSLv3 TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers RC4:HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;


       location /
       {
            proxy_pass  https://kalle:3004;
        }
    }
 
