var handler = {}

handler.message = function(object) {
  var safe_message = $('<div/>').text(object.msg).html();
  safe_message = replaceURLWithHTMLLinks(safe_message);
  var safe_from = $('<div/>').text(object.nick).html();
  return chatboxAppend(safe_from, safe_message, 'msg')
};

handler.join = function(object) {
  var safe_from = $('<div/>').text(object.from).html();
  $('#nicklist').append('<div class="name">' + safe_from + '</div>') ;
  return chatboxAppend(safe_from, 'joined', 'join')
};

handler.quit = function(object) {
  var safe_from = $('<div/>').text(object.from).html();
  $(getNicklistElement(safe_from)).remove();
  return chatboxAppend(safe_from, 'quit', 'quit')
};

handler.nicklist = function(object) {
  Object.keys(object.nicklist).forEach(function (nick) {
    var hash_from = btoa(nick).replace(/=/g,'_');
    $('#nicklist').append('<div class="name">' + nick + '</div>') ;
  });
};

handler.nickchange = function(object) {
  var safe_from = $('<div/>').text(object.nick).html();
  var safe_newnick = $('<div/>').text(object.newnick).html();
  $(getNicklistElement(safe_from)).remove();
  $('#nicklist').append('<div class="name">' + safe_newnick + '</div>') ;
  return chatboxAppend(safe_from, 'is now known as ' + safe_newnick, 'nick');
};
