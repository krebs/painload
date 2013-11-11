var handler = {}

handler.message = function(object) {
  var safe_message = $('<div/>').text(object.msg).html();
  safe_message = replaceURLWithHTMLLinks(safe_message);
  var safe_from = $('<div/>').text(object.nick).html();
  return chatboxAppend(safe_from, safe_message)
};

handler.join = function(object) {
  var safe_from = $('<div/>').text(object.from).html();
  $('<tr><td class="chat_date">'+getCurTime()+'</td><td class="chat_from">'+safe_from+'</td><td class="chat_msg" style="color:#00FF00">joined</td></tr>').insertBefore('#foot');
  $('#nicklist').append('<div class="name">' + safe_from + '</div>') ;
};

handler.quit = function(object) {
  var safe_from = $('<div/>').text(object.from).html();
  $('<tr><td class="chat_date">'+getCurTime()+'</td><td class="chat_from">'+safe_from+'</td><td class="chat_msg" style="color:#FF0000">quit</td></tr>').insertBefore('#foot');
  console.log('removing', safe_from);
  $(getNicklistElement(safe_from)).remove();
};

handler.nicklist = function(object) {
  Object.keys(object.nicklist).forEach(function (nick) {
//  console.log('nick',nick);
    var hash_from = btoa(nick).replace(/=/g,'_');
//    $('.name').each(function (i,e) { console.log(i,e); if (e.innerHTML === 'kweb') { $(e).attr("style", "color:green") } })
    $('#nicklist').append('<div class="name">' + nick + '</div>') ;
  });
};

handler.nickchange = function(object) {
  var safe_from = $('<div/>').text(object.nick).html();
  var safe_newnick = $('<div/>').text(object.newnick).html();
  $('<tr><td class="chat_date">'+getCurTime()+'</td><td class="chat_from">'+safe_from+'</td><td class="chat_msg">is now known as '+object.newnick+'</td></tr>').insertBefore('#foot');
  $(getNicklistElement(safe_from)).remove();
  $('#nicklist').append('<div class="name">' + safe_newnick + '</div>') ;
};
