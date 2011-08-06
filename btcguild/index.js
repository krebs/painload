api_key = process.env.api_key;

var options = {
  host: 'www.btcguild.com',
  port: 80,
  path: '/api.php?api_key=' + api_key
};

http = require('http');
http.get(options, function(res) {
  var data = '';
  res.on('data', function (chunk) {
    data += chunk;
  });
  res.on('end', function () {
    console.log(JSON.parse(data));
  });
}).on('error', function(e) {
  console.error('Error: ' + e.message);
});
