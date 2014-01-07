# go - minimalistic uri shortener

## install dependencies

    npm install

  apparently you can also

    npm install hiredis

  for more awesome.

## run service

    PORT=80 node .

  if you omit `PORT`, then it's `1337`.

  there's also the possibility to change the Redis key prefix which
  defaults to `go:` with

    REDIS_KEY_PREFIX=foobarmyprefix/

  to generate slightly more informative shortened uris set

    NOT_SO_SHORT=true

## add uri

    curl -F uri=https://mywaytoolonguri http://localhost:1337

  this will give you a shortened uri.

## resolve uri

    curl -L http://localhost:1337/1

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
