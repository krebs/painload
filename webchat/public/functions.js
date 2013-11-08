function inputParser (str) {
  var match = /^\/([a-z]+)(?:\s+(.*\S))?\s*$/.exec(str)
  if (match) {
    return { method: match[1], params: match[2] }
  } else {
    return { method: 'say', params: str }
  }
}


function clientParser(object) {
  console.log(object)
  switch (object.type) {
    case 'message':
      return printMessage(object);
    case 'join':
      return handleJoin(object);
    case 'quit':
      return handleQuit(object);
    case 'nicklist': 
      return handleNicklist(object);
    case 'nickchange':
      return handleNickchange(object);
  }
};

function handleJoin(object) {
  var safe_from = $('<div/>').text(object.from).html();
  $('<tr><td class="chat_date">'+getCurTime()+'</td><td class="chat_from">'+safe_from+'</td><td class="chat_msg" style="color:#00FF00">joined</td></tr>').insertBefore('#foot');
  $('#nicklist').append('<div class="name">' + safe_from + '</div>') ;
};

function handleQuit(object) {
  var safe_from = $('<div/>').text(object.from).html();
  $('<tr><td class="chat_date">'+getCurTime()+'</td><td class="chat_from">'+safe_from+'</td><td class="chat_msg" style="color:#FF0000">quit</td></tr>').insertBefore('#foot');
  console.log('removing', safe_from);
  $(getNicklistElement(safe_from)).remove();
};

function handleNicklist(object) {
  Object.keys(object.message).forEach(function (nick) {
//  console.log('nick',nick);
    var hash_from = btoa(nick).replace(/=/g,'_');
//    $('.name').each(function (i,e) { console.log(i,e); if (e.innerHTML === 'kweb') { $(e).attr("style", "color:green") } })
    $('#nicklist').append('<div class="name">' + nick + '</div>') ;
  });
};

function handleNickchange(object) {
  var safe_from = $('<div/>').text(object.nick).html();
  var safe_newnick = $('<div/>').text(object.newnick).html();
  $('<tr><td class="chat_date">'+getCurTime()+'</td><td class="chat_from">'+safe_from+'</td><td class="chat_msg">is now known as '+object.newnick+'</td></tr>').insertBefore('#foot');
  $(getNicklistElement(safe_from)).remove();
  $('#nicklist').append('<div class="name">' + safe_from + '</div>') ;
};

function replaceURLWithHTMLLinks (text) {
  var exp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
  return text.replace(exp,"<a class=chat_link href='$1'>$1</a>");
}

function setMaybeNick (input) {
  if (match) {
    nick = match[1];
    $('#nick').html(nick);
  }
}
function sortNicklist () {
};

function getNicklistElement(name) { 
  var el;
  $('.name').each(function (i,e) {
    if (e.innerHTML === name) {
      if (typeof el !== 'undefined') {
        throw new Error('duplicate name: ' + name);
      };
      el = e;
    };
  });
  return el;
}

function chatboxAppend (chat_from, chat_msg, type) {
  type = type||'chat'
  $('<tr><td class="'+type+'_date">'+getCurTime()+'</td><td class="'+type+'_from">'+chat_from+'</td><td class="'+type+'_msg">'+chat_msg+'</td></tr>').insertBefore('#foot');

  var elem = document.getElementById('chatter');
  elem.scrollTop = elem.scrollHeight;
};

function printMessage(object) {
  var safe_message = $('<div/>').text(object.message).html();
  safe_message = replaceURLWithHTMLLinks(safe_message);
  var safe_from = $('<div/>').text(object.nick).html();
  return chatboxAppend(safe_from, safe_message)
};

function getCurTime () {
  date = new Date;
  h = date.getHours();
  if(h<10)
  {
    h = "0"+h;
  }
  m = date.getMinutes();
  if(m<10)
  {
    m = "0"+m;
  }
  s = date.getSeconds();
  if(s<10)
  {
    s = "0"+s;
  }
  return ''+h+':'+m+':'+s;
};
