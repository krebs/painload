

var serverCommands = {};
serverCommands.say = function (settings, params) {
  var nick = settings.nick
  var message = params.msg
  params.nick = nick
  irc_client.say("#krebs", nick + ' → ' + message);
  return clients.notifyAll('message', params)
}

serverCommands.nick = function (settings, params) {
  var oldnick = settings.nick
  var newnick = params.nick
  settings.nick = newnick
  return clients.notifyAll('nickchange', { nick: oldnick, newnick: newnick });
}

serverCommands.badcommand = function (settings, params) {
  settings.conn.write(JSON.stringify({ method: 'usererror', params: { message: 'bad command' }}))
}

module.exports = serverCommands
