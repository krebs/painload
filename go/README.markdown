# go - minimalistic uri shortener

## install dependencies

    npm install

  apparently you can also

    npm install hiredis

  for more awesome.

## run service

    HOSTN=go PORT=80 node .

  if you omit `HOSTN`, then relative shortened uris will be generated.
  if you omit `PORT`, then it's `1337`.

## add uri

    curl -F uri=https://mywaytoolonguri http://go

  this will give you a shortened uri.

## resolve uri

    curl -L http://go/1

## clear database

    redis-cli keys 'go:*' | xargs redis-cli del

  if you have changed `redisPrefix`, then use that instead of `go:`.

## use systemd

  run

    make install

  to install the systemd service and configuration files.
  this will fail if the files are already installed and modified.

  configure `HOSTN` and `PORT` in `/etc/conf.d/go.env` and the user
  and/or group in `/etc/systemd/system/go.service`.

  and finally start the service with

    systemctl start go

  if you want to run as an unprivileged user but still want to use
  port `80`, then maybe try something like

    iptables -t nat -A PREROUTING -p tcp --dport 1337 -j REDIRECT --to-ports 80
