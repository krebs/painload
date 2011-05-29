
nick = /(^|\n) *Name *= *(\S*) *($|\n)/
    .exec(require('fs').readFileSync('/etc/tinc/retiolum/tinc.conf'))[2];

var config = {
  "nick": nick + '-krebs',
  "server": "irc.freenode.net",
  "port": 6667,
  "channel": "#tincspasm"
};

irc = require('./lib/irc').createClient(config);

// TODO call back when joined
irc.connect(function () {
  console.log('like a boss: ' + nick);
  //irc.write();
});
