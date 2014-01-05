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
