var hostname = process.env.HOSTN;
var httpPort = process.env.PORT || 1337;
var redisPrefix = 'go:';
var uriPrefix = '';
if (hostname) {
  uriPrefix += 'http://' + hostname;
  if (httpPort != 80) {
    uriPrefix += ':' + httpPort;
  }
}

var http = require('http');
var formidable = require('formidable');
var redis = require('redis');

var redisClient = redis.createClient();
var httpServer = http.createServer(listener);

redisClient.on('error', function (err) {
  console.log('redis made a bubu:', err.message);
  process.exit(23);
});
httpServer.listen(httpPort, function () {
  console.log('http server listening on port', httpPort);
});

function listener (req, res) {
  if (req.method === 'POST' && req.url === '/') {
    return create(req, res);
  } else if (req.method === 'GET') {
    return retrieve(req, res);
  } else {
    return methodNotAllowed(req, res);
  }
}

function create (req, res) {
  redisClient.incr(redisPrefix + 'index', function (err, reply) {
    if (err) {
      return internalError(err, req, res);
    }

    var form = new formidable.IncomingForm();

    form.parse(req, function(err, fields, files) {
      if (err) {
        return internalError(err, req, res);
      }

      var uri = fields.uri;
      // TODO check uri(?)
      var shortPath = '/' + reply;
      var shortUri = uriPrefix + shortPath;
      var key = redisPrefix + shortPath;

      redisClient.set(key, uri, function (error) {
        if (error) {
          return internalError(err, req, res);
        }

        res.writeHead(200, { 'content-type': 'text/plain' });
        return res.end(shortUri + '\r\n');
      });
    });
  });
}

function retrieve (req, res) {
  var key = redisPrefix + req.url;
  redisClient.get(key, function (error, reply) {
    if (error) {
      return internalError(err, req, res);
    }
    
    if (typeof reply !== 'string') {
      res.writeHead(404, { 'content-type': 'text/plain' });
      return res.end('not found\r\n');
    }

    res.writeHead(302, {
      'content-type': 'text/plain',
      'location': reply,
    });
    return res.end();
  });
}

function methodNotAllowed (req, res) {
  res.writeHead(405, { 'content-type': 'text/plain' });
  return res.end('method not allowed\r\n');
}
function internalError (error, req, res) {
  res.writeHead(500, { 'content-type': 'text/plain' });
  return res.end(error.message + '\r\n');
}
