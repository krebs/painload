'use strict';
var fs = require('fs');
var http = require('https');
var sockjs = require('sockjs');
var connect = require('connect');
var irc = require('irc');
var make_sockjs_server_connection_transport = require('./sockjs_server_connection_transport.js')
var RPC = require('./public/rpc.js');
var irc_nicks = []

function pluck (key) {
  return function (object) {
    return object[key]
  }
}

var clients = [];
clients.broadcast = function (method, params) {
  clients.map(pluck('rpc')).forEach(function (rpc) {
    rpc.send(method, params)
  })
}

var irc_reconnect = function() { //reconnt to irc
  console.log("would reconnect now")
//  irc_client.disconnect()
//  irc_client.connect()
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
  clients.broadcast('msg', {nick: from, msg: message})
  clearTimeout(lastping);
});

irc_client.on('names#krebs', function(nicks) {
  Object.keys(nicks).forEach(function (nick) {
  irc_nicks.push(nick)
    clients.broadcast('join', {type: 'irc', nick: nick})
  })
})

irc_client.on('join#krebs', function(nick, msg) {
  if (nick !== 'kweb'){
    irc_nicks.push(nick)
    clients.broadcast('join', {type: 'irc', nick: nick})
  }
})

irc_client.on('part#krebs', function(nick, rs, msg) {
  clients.broadcast('part', {type: 'irc', nick: nick})
});

irc_client.on('error', function (error) {
  irc_nicks.forEach( function(nick) {
    client.rpc.send('part', {type: 'irc', nick: nick})
    irc_nicks.splice(irc_nicks.indexOf(nick))
  })
  console.log('irc-client error', error)
})

var echo = sockjs.createServer();

var total_clients_ever_connected = 0

echo.on('connection', function (connection) {
  var client = {}
  client.rpc = new RPC(make_sockjs_server_connection_transport(connection))
  client.nick = 'anon'+(++total_clients_ever_connected)
  client.rpc.send('your_nick', {nick: client.nick}) 
  client.rpc.register('msg', {msg: 'string'}, function (params, callback) {
    callback(null)
    clients.broadcast('msg', {type: 'web', nick: client.nick, msg: params.msg})
    irc_client.say('#krebs', client.nick + ' → ' + params.msg)
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
      clients.broadcast('nick', {type: 'web', newnick: client.nick, oldnick: oldnick})
      irc_client.say('#krebs', oldnick + ' is now known as ' + client.nick)
    }
  })
  connection.on('close', function() { //propagate if client quits the page
    clients.splice(clients.indexOf(client));
    clients.broadcast('part', {type: 'web', nick: client.nick})
    irc_client.say('#krebs', client.nick + ' has parted')
  })
  //send the irc nicklist to the new joined client
  irc_nicks.forEach( function(nick) {
    client.rpc.send('join', {type: 'irc', nick: nick})
  })
  //send nicklist to newly joined client
  clients.map(pluck('nick')).forEach(function (nick) {
    client.rpc.send('join', {type: 'web', nick: nick}) 
  })
  //add new client to list
  clients.push(client)
  //send all including the new client the join
  clients.broadcast('join', {type: 'web', nick: client.nick})
  //send join to irc
  irc_client.say('#krebs', client.nick + ' has joined')
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

var web_serv_options = { //certificates for https
  key: fs.readFileSync(__dirname+'/local_config/server_npw.key'),
  cert: fs.readFileSync(__dirname+'/local_config/server.crt'),
};
var server = http.createServer(web_serv_options, app);
echo.installHandlers(server, {prefix:'/echo'});
server.listen(1337, '0.0.0.0');
console.log('Server running at https://127.0.0.1:1337/');
