var serverCommands = {};

serverCommands.coi = function (serverstate, settings, params, id) {
  return settings.conn.write({ result: { nick: settings.nick, addr: settings.addr}, id: id})
}

serverCommands.say = function (serverstate, settings, params, id) {
  var nick = settings.nick
  var message = params.msg
  params.nick = nick
  serverstate.irc_client.say("#krebs", nick + ' → ' + message);
  return serverstate.clients.notifyAll('message', params)
}

serverCommands.nick = function (serverstate, settings, params, id) {
  var oldnick = settings.nick
  var newnick = params.nick
  settings.nick = newnick
  return serverstate.clients.notifyAll('nickchange', { nick: oldnick, newnick: newnick });
}

serverCommands.badcommand = function (serversate, settings, params, id) {
  settings.conn.write(JSON.stringify({ method: 'usererror', params: { message: 'bad command' }}))
}

module.exports = serverCommands
