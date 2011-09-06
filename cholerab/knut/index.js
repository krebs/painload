#! /usr/bin/env node

var host = process.env.host || '127.0.0.1';
var port = Number(process.env.port) || 42101;

var pipe = '/tmp/krebscode.painload.cholerab.ttycnser.' + process.env.LOGNAME;

var fs = require('fs');
var http = require('http');
var slurp = require('./src/io/slurp');
var spawn = require('child_process').spawn;

var plugs = process.argv.slice(2);

if (plugs.length === 0) {
  console.error('Error 1: You are made of stupid!'
      + '\nPro-Tip: [32m'
      + require('path').basename(process.argv[1]) + ' [31;1mPLUG[m'
      + ' # PLUG ∈ {'
      + require('fs').readdirSync(__dirname + '/plugs').join(',')
      + '}^n, n ≥ 1');
  process.exit(23);
};

http.createServer(function (req, res) {
  return slurp(req, function (data) {
    try {
      var message = JSON.parse(data);
    } catch (exn) {
      console.error(exn.stack);
    };
    if (message) {
      plugs.forEach(function (plug) {

        var env = JSON.parse(JSON.stringify(process.env));
        Object.keys(message).forEach(function (key) {
          env[key] = message[key];
        });

        var child = spawn(__dirname + '/plugs/' + plug + '/index', [], {
          env: env
        });

        child.stdout.on('data', function (data) {
          console.log(plug, 'stdout:', data.toString());
        });

        child.stderr.on('data', function (data) {
          console.log(plug, 'stderr:', data.toString());
        });

        child.on('exit', function (code) {
          console.log(plug, 'exit:', code);
          if (code === 0) {
            res.writeHead(200, { 'Content-Length': 0 });
            res.end();
          } else {
            res.writeHead(500, { 'Content-Length': 0 });
            res.end();
          };
        });

      });
    } else {
      res.writeHead(400, 'You are made of stupid!', {
        'Content-Length': 0
      });
      res.end();
    };
  });
}).listen(port, host, function () {
  console.log('Serving HTTP on', host, 'port', port);
});
