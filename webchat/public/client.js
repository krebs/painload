var settings = {}

$(function updateTime () {
  $('#time').html(getCurTime());
  setTimeout(updateTime,'1000');
  return true;
});

settings.waiting_callbacks = {}

$(function connect() {
  settings.sock = new SockJS('/echo');
  var transport = make_sockjs_client_transport(settings.sock)
  var rpc = new RPC(transport)
  rpc.register('msg', {type: 'string', nick: 'string', msg: 'string'}, function(params, callback) {
    var safe_message = $('<div/>').text(params.msg).html();
    safe_message = replaceURLWithHTMLLinks(safe_message);
    var safe_from = $('<div/>').text(params.nick).html();
    chatboxAppend(safe_from, safe_message, 'web_msg')
    return callback(null)
  })
  rpc.register('nick', {type: 'string', newnick: 'string', oldnick: 'string'}, function(params, callback) {
    var safe_oldnick = $('<div/>').text(params.oldnick).html();
    var safe_newnick = $('<div/>').text(params.newnick).html();
    var safe_type = $('<div/>').text(params.type).html();
    if (safe_oldnick === settings.nick){
      settings.nick = safe_newnick
      $('#nick').html(settings.nick)
    }
    $(getNicklistElement(safe_oldnick,safe_type)).remove();
    $('#nicklist').append('<div class="'+safe_type+'_name">' + safe_newnick + '</div>') ;
    chatboxAppend(safe_oldnick, 'is now known as ' + safe_newnick, 'nick');
    return callback(null)
  })
  rpc.register('your_nick', {nick: 'string'}, function(params, callback) {
    var safe_nick = $('<div/>').text(params.nick).html();
    settings.nick = safe_nick
    $('#nick').html(settings.nick)
    return callback(null)
  })
  rpc.register('join', {type: 'string', nick: 'string'}, function(params, callback) {
    var safe_nick = $('<div/>').text(params.nick).html();
    var safe_type = $('<div/>').text(params.type).html();
    $('#nicklist').append('<div class="'+safe_type+'_name">' + safe_nick + '</div>') ;
    chatboxAppend(safe_nick, 'has joined');
    return callback(null)
  })
  rpc.register('part', {type: 'string', nick: 'string'}, function(params, callback) {
    var safe_nick = $('<div/>').text(params.nick).html();
    var safe_type = $('<div/>').text(params.type).html();
    $(getNicklistElement(safe_nick,safe_type)).remove();
    chatboxAppend(safe_nick, 'has parted');
    return callback(null)
  })
});
$(function() {
  $('#input').keydown(function(e) {
    if (e.keyCode === 13) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      var input = ($('#input').val());
      $('#input').val('');

      var command = inputParser(input)
      return (commands[command.method] || commands.badcommand)(settings, command.params)
    }
  });

});
