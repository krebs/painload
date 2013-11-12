var commands = {}

commands.msg = function (settings, params) {
  var sendObj = {
    method: 'msg',
    params: { msg: params }
  }
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
  console.log("error", params);
  chatboxAppend( '<span class="from_system">error</span>', 'command not found' )

  
}
