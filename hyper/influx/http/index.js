#! /usr/bin/env node

name = '//hyper/influx/http'
port = process.env.port || 1337
host = process.env.host || '127.0.0.1'


console.info(name);

fs = require('fs');
path = require('path');
http = require('http');

fifo_path = path.resolve(process.argv[2] || path.join(process.cwd(), '0'));

// check configuration
try {
  (function (stat) {
    if ((stat.mode & 0010000) === 0) {
      throw { code: 'E_not_fifo', path: fifo_path };
    };
  })(fs.statSync(fifo_path));
} catch (exn) {
  console.error(exn);
  process.exit(23);
};

process.stdin.destroy();
fifo = fs.createWriteStream(fifo_path);
fifo.on('open', function (fd) {
  console.info('fifo open as fd', fd);

  http.createServer(function (req, res) {
    var rhost = req.connection.remoteAddress;
    var rport = req.connection.remotePort;
    var id = rhost + ':' + rport;
  
    console.info(id, 'request', req.method, req.url);

    req.on('data', function (data) {
      console.info(id, 'data', data.length);
    });

    req.on('end', function (data) {
      console.info(id, 'end');
      res.writeHead(202, {
        'Content-Length': 0,
        'Connection': 'close'
      });
      res.end();
    });

    req.pipe(fifo, { end: false });
  }).listen(port, host, function () {
    console.info('server running at http://' + host + ':' + port + '/');
  });
});
