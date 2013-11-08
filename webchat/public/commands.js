var commands = {}

commands.say = function (settings, params) {
  var sendObj = {
    method: 'say',
    params: { message: params },
  };
  sock.send(JSON.stringify(sendObj))
}

commands.nick = function (settings, params) {
  settings.nick = params
  var sendObj = {
    method: 'nick',
    params: { nick: params },
  }
  sock.send(JSON.stringify(sendObj))
}

commands.badcommand = function (settings, params) {
  console.log("error");
  chatboxAppend( '<span class="from_system">error</span>', 'command not found' )

  
}
