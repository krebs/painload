
var Client = function (config) {
  var client = this;
  var net = require('net');
  var sys = require('sys');
  var log = function (x) {
    sys.puts('TCP server: ' + x);
  };

  client.connect = function (callback) {
    var stream = net.createConnection(config.port, config.server);
    stream.on('connect', function () {
      stream.write(
        'NICK ' + config.nick + '\n' +
        'USER ' + config.nick + ' 0 *:Karl Koch\n' +
        'JOIN ' + config.channel + '\n'
      );
      //client.write = function (text) {
      //  stream.write('PRIVMSG ' + config.channel + ' :' + text);
      //};
      client.write = msg_start_send;
      callback();
    });
    //stream.on('secure', function () {
    //});

    var msg = [];

    var msg_start_send = function (x) {
      client.write = msg_append;
      setTimeout(function () {
        var x = msg.join('\n') + '\n';
        msg = [];
        client.write = msg_start_send;
        stream.write('PRIVMSG ' + config.channel + ' :' + x);
      }, 1000);
    };

    var msg_append = function (x) {
      msg[msg.length] = x;
    };


    stream.on('data', function (data) {
      data = String(data);
      log('[35m' + data + '[m');
      if (data.substring(0,4) === 'PING') {
        log('PONG!');
        stream.write('PONG ' + data.substring(4));
      }
    });
    //stream.on('end', function () {
    //});
    //stream.on('timeout', function () {
    //});
    //stream.on('drain', function () {
    //});
    //stream.on('error', function (exception) {
    //});
    //stream.on('clonse', function (exception) {
    //});
  };
};

exports.createClient = function (config) {
  return new Client(config);
};
