
var connect = require('genericore').connect;

var config = {
  irc: {}
};

connect(config.irc, {
  debug: function (message) {
  },
  ready: function (client) {

  }
});



// {
//     userName: 'nodebot',
//     realName: 'nodeJS IRC client',
//     port: 6667,
//     debug: false,
//     showErrors: false,
//     autoRejoin: true,
//     channels: [],
//     secure: false
// }

var config = {
  "irc": {
    "nick": "a43243afds",
    "server": "irc.freenode.net",
    "port": 6667,
    "channel": "#genericoredump"
  },
  "amqp": {
    "reconnect_timeout": 10000,
    "connection": {
      "host": "141.31.8.11",
      "port": 5672,
      "login": "shack",
      "password": "shackit",
      "vhost": "/"
    },
    "exchange": {
      "name": "log",
      "options": {
        "type": "fanout",
        "passive": false,
        "durable": false,
        "auto_delete": false,
        "internal": false,
        "nowait": false
      }
    },
    "queue": {
      "name": "irclog2",
      "options": {
        "passive": false,
        "durable": false,
        "exclusive": false,
        "autoDelete": false,
        "nowait": false
      }
    }
  }
};

//var irc = require('./lib/irc');
var irc = require('./lib/irc').createClient(config.irc);
var amqp = require('amqp');

// TODO var amqp = require('./lib/amqp').createClient(config.amqp);
//  where createClient will bind to all connected (exchange,queue) pairs
// irc.connect({
//   ready: function () {
//     amqp.connect({
//       message: function (message) {
//         console.log(message);
//         irc.privmsg(config.irc.channel, message.data);
//       }
//     });
//   }
// });

// TODO call back when joined
irc.connect(function () {
  var connection = amqp.createConnection(config.amqp.connection);
  connection.on('ready', function () {
    var queue = connection.queue(config.amqp.queue.name, config.amqp.queue.options);

    queue.bind(config.amqp.exchange.name, config.amqp.queue.name);

    console.log('receiving messages');
    queue.subscribe(function (message) {
      console.log(message.data);
      irc.write(message.data);
    });
  });
});

// amqp.connect(function () {
//   amqp.connection.exchange("log", config.amqp.exchange.options).on(
//     'open', function () {
//       log = function (message) {
//         exchange.publish(config.amqp.exchange.name, message);
//       };
//     }
//   );
// 
//   tcp.serve(function (message) {
//     var data = parse(message);
//     log('[mailsrc,tcp] incoming: ' + data['Header-Fields']['Subject']);
//     console.log('publishing: ' + data['Header-Fields'].From);
//     amqp.publish({ type: 'mail', subtype: 0, data: data });
//   });
// });
// 
// 
// var client = new irc.Client(config.server, config.nick, {
//   channels: [config.channel],
// });
// 
// client.on('error', function (err) {
//   console.log('>>>\n' + require('sys').inspect(err));
// });
// 
// 
// var amqp = require('amqp');
// client.join(config.channel, function () {
// 
//   var connection = amqp.createConnection(config.amqp.connection);
// 
//   // Wait for connection to become established.
//   connection.on('ready', function () {
//     // Create a queue and bind to all messages.
//     // Use the default 'amq.topic' exchange
//     var q = connection.queue(config.amqp.queue.name, config.amqp.queue);
//     // Catch all messages
//     q.bind(config.amqp.exchange.name, config.amqp.queue.name);
// 
//     // Receive messages
//     console.log('receiving messages');
//     q.subscribe(function (message) {
//       // Print messages to stdout
//       console.log(message);
//       client.say(config.channel, message.data);
//     });
//   });
// });
 




// client.on('pm', function (from, message) {
//   sys.puts(from + ' => ME: ' + message);
// });
// 
// client.on('message#yourchannel', function (from, message) {
//   sys.puts(from + ' => #yourchannel: ' + message);
// });
