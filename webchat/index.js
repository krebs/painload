var fs = require('fs');
var http = require('https');
var sockjs = require('sockjs');
var connect = require('connect');
var irc = require('irc');
var Clients = [];

Clients.broadcast = function(object) { //broadcast to all clients
  Clients.forEach(function(client) {
    client.write(JSON.stringify(object));
  });
}

var serverCommands = {};

serverCommands.say = function (settings, params) {
  var nick = settings.nick || settings.conn.remoteAddress
  var message = params.message
  irc_client.say("#krebs", nick + ' → ' + message);
  return Clients.broadcast({ type: 'message', nick: nick, message: message })
}

serverCommands.nick = function (settings, params) {
  var oldnick = settings.nick || settings.conn.remoteAddress
  var newnick = params.nick
  settings.nick = newnick
  return Clients.broadcast({ type: 'nickchange', nick: oldnick, newnick: newnick })
}

serverCommands.badcommand = function (settings, params) {
  settings.conn.write(JSON.stringify({ type: 'usererror', message: 'bad command' }))
}

var irc_reconnect = function() { //reconnt to irc
  console.log("reconnecting due to pingtimeout");
  irc_client.disconnect();
  irc_client.connect();
}

var pingTimeoutDelay = 3*60*1000
var lastping = setTimeout(irc_reconnect, pingTimeoutDelay)

var irc_client = new irc.Client('irc.freenode.net', 'kweb', { //create irc_client to talk to irc
  channels: ['#krebs'], //todo: read from local_config
  sasl: true, 
  secure: true,
  userName: 'kweb', //todo: read from local_config
  realName: 'kweb', //todo: read from local_config
  password: fs.readFileSync(__dirname+'/local_config/irc.key').toString(),
  debug: false,
  showErrors: true,
  floodProtection: true,
  port: 6697,
  autoRejoin: true,
  autoConnect: true,
  stripColors: true
});


irc_client.on('ping', function(server) { //restart timer on server ping
  console.log("got ping from server, renewing timeout for automatic reconnect");
  clearTimeout(lastping);
  lastping = setTimeout(irc_reconnect, pingTimeoutDelay); //reconnect after irc timeout
})

irc_client.on('message#krebs', function(from, message) {
  console.log({ from: from, message: message });
  Clients.broadcast({ type: 'message', from: from, message: message }); //broadcast irc messages to all connected clients
  clearTimeout(lastping);
});

irc_client.on('names#krebs', function(nicks) {
  Clients.broadcast({type: 'nicklist', message: nicks});
});

irc_client.on('join#krebs', function(nick, msg) {
  if (nick !== 'kweb'){
    Clients.broadcast({type: 'join', from: nick});
  }
});

irc_client.on('part#krebs', function(nick, rs, msg) {
  Clients.broadcast({type: 'quit', from: nick});
});

var web_serv_options = { //certificates for https
  key: fs.readFileSync(__dirname+'/local_config/server_npw.key'),
  cert: fs.readFileSync(__dirname+'/local_config/server.crt'),
};

var echo = sockjs.createServer();
echo.on('connection', function(conn) {
  var origin = conn.remoteAddress;
  var settings = {
    conn: conn
  }
  Clients.push(conn);
  Clients.broadcast({type: 'join', from: origin})
//  irc_client.say("#krebs", origin + ' has joined');
  if (typeof irc_client.chans['#krebs'] === 'object') {
    conn.write(JSON.stringify({type: 'nicklist', message: irc_client.chans['#krebs'].users})); //send current nicklist
  };
  conn.write(JSON.stringify({type: 'message', from: 'system', message: 'hello' })) //welcome message
  console.log(irc_client.chans['#krebs'])
  conn.on('data', function(data) {
    console.log('data:',data);
    try {
      var command = JSON.parse(data);
      return (serverCommands[command.method] || serverCommands.badcommand)(settings, command.params)

    } catch (error) {
      console.log(error);
    }
  });
  conn.on('close', function() { //propagate if client quits the page
  Clients.splice(Clients.indexOf(conn));
  Clients.broadcast({type: 'quit', from: origin})
//  irc_client.say("#krebs", origin + ' has quit');
});
});


var app = connect()
  .use(connect.logger('dev'))
  .use(connect.static(__dirname+'/public'))
  .use( function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    page_template='<!doctype html>\n';
    page_template+='<link rel="stylesheet" type="text/css" href="reset.css">\n';
    page_template+='<script src="sockjs-0.3.min.js"></script>\n';
    page_template+='<script src="jquery-2.0.3.min.js"></script>\n';
    page_template+='<script src="commands.js"></script>\n';
    page_template+='<script src="functions.js"></script>\n';
    page_template+='<script src="client.js"></script>\n';
    page_template+='<div id="bg">';
    page_template+='<div id="chatter">';
    page_template+='<div id="space"></div>';
    page_template+='hello, this is the official krebs support:<br>\n';
    page_template+='<table id="chatbox"><tr id="foot"><td id="time"></td><td id="nick" class="chat_from"></td><td><input type="text" id="input"></td></tr></table>\n';
    page_template+='</div>';
    page_template+='<div id="sideboard"><div id=nicklist></div>';
    page_template+='<div id="links">';
    page_template+='<a href="http://gold.krebsco.de/">krebsgold browser plugin</a><br>';
    page_template+='<a href="http://ire:1027/dashboard/">ire: Retiolum Dashboard</a><br>';
    page_template+='<a href="http://pigstarter/">pigstarter: network graphs</a><br>';
    page_template+='</div></div></div>';
    res.end(page_template);

  })
var server = http.createServer(web_serv_options, app);
echo.installHandlers(server, {prefix:'/echo'});
server.listen(1337, '0.0.0.0');
console.log('Server running at https://127.0.0.1:1337/');
