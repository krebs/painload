'use strict';
var fs = require('fs');
var http = require('https');
var sockjs = require('sockjs');
var connect = require('connect');
var irc = require('irc');
var make_sockjs_server_connection_transport = require('./sockjs_server_connection_transport.js')
var RPC = require('./public/rpc.js');

var clients = [];

var irc_reconnect = function() { //reconnt to irc
  console.log("reconnecting due to pingtimeout")
  irc_client.disconnect()
  irc_client.connect()
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
  debug: true,
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
  clients.map(pluck('rpc')).forEach(function (rpc) {
    rpc.send('msg', {nick: from, msg: message})
  })
  clearTimeout(lastping);
});

irc_client.on('names#krebs', function(nicks) {
  clients.map(pluck('rpc')).forEach(function (rpc) {
    Object.keys(nicks).forEach(function (nick) {
      rpc.send('join', {type: 'irc', nick: nick})
    })
  })
});

irc_client.on('join#krebs', function(nick, msg) {
  if (nick !== 'kweb'){
    clients.map(pluck('rpc')).forEach(function (rpc) {
      rpc.send('join', {type: 'irc', nick: nick})
    })
  }
})

irc_client.on('part#krebs', function(nick, rs, msg) {
  clients.map(pluck('rpc')).forEach(function (rpc) {
    rpc.send('part', {type: 'irc', nick: nick})
  })
});

irc_client.on('error', function (error) {
  console.log('irc-client error', error)
})

var web_serv_options = { //certificates for https
  key: fs.readFileSync(__dirname+'/local_config/server_npw.key'),
  cert: fs.readFileSync(__dirname+'/local_config/server.crt'),
};

var echo = sockjs.createServer();

function pluck (key) {
  return function (object) {
    return object[key]
  }
}
var total_clients_ever_connected = 0

echo.on('connection', function (connection) {
  var client = {}
  client.rpc = new RPC(make_sockjs_server_connection_transport(connection))
  client.nick = 'anon'+(++total_clients_ever_connected)
  client.rpc.send('your_nick', {nick: client.nick}) 
  client.rpc.register('msg', {msg: 'string'}, function (params, callback) {
    callback(null)
    clients.map(pluck('rpc')).forEach(function (rpc) {
      rpc.send('msg', {type: 'web', nick: client.nick, msg: params.msg})
    })
  })
  client.rpc.register('nick', {nick: 'string'}, function (params, callback) {
    if (!!~clients.map(pluck('nick')).indexOf(params.nick)) {
      callback('name already taken')
    } else if (/^anon[0-9]+$/.test(params.nick)) {
      callback('bad nick')
    } else {
      var oldnick = client.nick
      client.nick = params.nick
      callback(null)
      clients.map(pluck('rpc')).forEach(function (rpc) {
        rpc.send('nick', {type: 'web', newnick: client.nick, oldnick: oldnick})
      })
    }
  })
  connection.on('close', function() { //propagate if client quits the page
    clients.splice(clients.indexOf(client));
    clients.map(pluck('rpc')).forEach(function (rpc) {
      rpc.send('part', {type: 'web', nick: client.nick})
    })
  })
  //send nicklist to newly joined client
  clients.map(pluck('nick')).forEach(function (nick) {
    client.rpc.send('join', {type: 'web', nick: nick}) 
  })
  //add new client to list
  clients.push(client)
  //send all including the new client the join
  clients.map(pluck('rpc')).forEach(function (rpc) {
    rpc.send('join', {type: 'web', nick: client.nick})
  })

})

var app = connect()
  .use(connect.logger('dev'))
  .use(connect.static(__dirname+'/public'))
  .use( function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    var page_template='<!doctype html>\n';
    page_template+='<link rel="stylesheet" type="text/css" href="reset.css">\n';
    page_template+='<script src="sockjs-0.3.min.js"></script>\n';
    page_template+='<script src="jquery-2.0.3.min.js"></script>\n';
    page_template+='<script src="commands.js"></script>\n';
    page_template+='<script src="functions.js"></script>\n';
    page_template+='<script src="sockjs_client_transport.js"></script>\n';
    page_template+='<script src="rpc.js"></script>\n';
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
