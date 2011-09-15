require('http').createServer(function (req, res) {

  req.on('data', function (data) {
    require('util').puts(data);
  });

  req.on('end', function () {
    res.writeHead(200, {'Content-Type': 'text/plain', 'Content-Length': 0});
    res.end();
  });
}).listen(1337, '127.0.0.1', function () {
  console.log('Running HyperSink at http://127.0.0.1:1337/');
});
