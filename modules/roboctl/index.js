var config = {
  "nick": "roboctl",
  "server": "irc.freenode.net",
  "port": 6667,
  "channel": "#tincspasm"
};

irc = require('./lib/irc').createClient(config);

// TODO call back when joined
irc.connect(function () {
  console.log('like a boss');
  //irc.write();
});
