var fs = require('fs');
var http = require('https');
var sockjs = require('sockjs');
var connect = require('connect');
var irc = require('irc');
var krebsimage = require('./krebs-img.js');
var Clients = [];
Clients.broadcast = function(object) {
  Clients.forEach(function(client) {
    client.write(JSON.stringify(object));
  });
}
var pingTimeoutDelay = 5*60*1000
var lastping = setTimeout(reconnect, pingTimeoutDelay)

var irc_client = new irc.Client('irc.freenode.net', 'kweb', {
  channels: ['#krebs'],
  sasl: true,
  secure: true,
  userName: 'kweb',
  realName: 'kweb',
  password: fs.readFileSync(__dirname+'/irc.key').toString(),
  debug: true,
  showErrors: true,
  port: 6697,
  autoRejoin: true,
  autoConnect: true
});

var reconnect = function() {
  console.log("reconnecting due to pingtimeout");
  irc_client.disconnect();
  irc_client.connect();
}

irc_client.on('ping', function(server) {
  console.log("got ping from server, renewing timeout for automatic reconnect");
  clearTimeout(lastping);
  lastping = setTimeout(reconnect, pingTimeoutDelay);
})

irc_client.on('message#krebs', function(from, message) {
  console.log({ from: from, message: message });
  Clients.broadcast({ from: from, message: message });
  clearTimeout(lastping);
});

var echo = sockjs.createServer();
echo.on('connection', function(conn) {
  var name = '['+conn.remoteAddress+':'+conn.remotePort+']';
  Clients.push(conn);
  Clients.broadcast({from: 'system', message: name + ' has joined'})
  irc_client.say("#krebs", name + ' has joined');
conn.write(JSON.stringify({from: 'system', message: 'hello'}))
  conn.on('data', function(message) {
    console.log('data:',message);
    try {
      var object = JSON.parse(message);
      object.from = name
    console.log(object.message);
  irc_client.say("#krebs", name + '→' + object.message);
  Clients.broadcast(object);

    } catch (error) {
      console.log(error);
    }
  });
conn.on('close', function() {
  Clients.splice(Clients.indexOf(conn));
  Clients.broadcast({from: 'system', message: name + ' has quit'})
  irc_client.say("#krebs", name + ' has quit');
});
});

var options = {
  key: fs.readFileSync(__dirname+'/server_npw.key'),
  cert: fs.readFileSync(__dirname+'/server.crt'),
};

var app = connect()
  .use(connect.logger('dev'))
  .use(connect.static(__dirname+'/public'))
  .use( function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.write('<!doctype html>');
    res.write('<link rel="stylesheet" type="text/css" href="reset.css">');
    res.write('<script src="sockjs-0.3.min.js"></script>');
    res.write('<script src="jquery-2.0.3.min.js"></script>');
    res.write('<script src="client.js"></script>');
    res.write(krebsimage+'<br>');
    res.write('hello, this is result:<br>');
    res.write('<table id="chatbox"></table>');
    res.end('<input type="text" id="input"><br>');

  })
var server = http.createServer(options, app);
echo.installHandlers(server, {prefix:'/echo'});
server.listen(1337, '0.0.0.0');
console.log('Server running at https://127.0.0.1:1337/');
