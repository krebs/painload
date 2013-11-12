
function replaceURLWithHTMLLinks (text) {
  var exp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
  return text.replace(exp,"<a class=chat_link href='$1'>$1</a>");
}

function getNicklistElement(name, type) { 
  var el;
  $('.'+type+'_name').each(function (i,e) {
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
  type = type||'msg'
  $('<tr><td class="date '+type+'_date">'+getCurTime()+'</td><td class="from '+type+'_from">'+chat_from+'</td><td class="msg '+type+'_msg">'+chat_msg+'</td></tr>').insertBefore('#foot');

  var elem = document.getElementById('chatter');
  elem.scrollTop = elem.scrollHeight;
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
