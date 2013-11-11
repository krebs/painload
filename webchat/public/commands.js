var commands = {}

commands.say = function (settings, params) {
  var sendObj = {
    method: 'say',
    params: { msg: params },
  };
  settings.sock.send(JSON.stringify(sendObj))
}

commands.nick = function (settings, params) {
  var sendObj = {
    method: 'nick',
    params: { nick: params },
  }
  settings.sock.send(JSON.stringify(sendObj))
}

commands.badcommand = function (settings, params) {
  console.log("error");
  chatboxAppend( '<span class="from_system">error</span>', 'command not found' )

  
}
