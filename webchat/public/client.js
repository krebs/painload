function replaceURLWithHTMLLinks (text) {
  var exp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
  return text.replace(exp,"<a href='$1'>$1</a>");
}
function setMaybeNick (input) {
  var match = /^\/nick\s+(.+)$/.exec(input);
  if (match) {
    nick = match[1];
  }
}

var nick;

$(function connect() {
  sock = new SockJS('/echo');

  sock.onopen = function() {
    console.log('open');
    sock.send('open');
  };
  sock.onmessage = function(e) {
    console.log('message', e.data);
    try {
      var object = JSON.parse(e.data);
      console.log(object.message);
      var safe_message = $('<div/>').text(object.message).html();
      safe_message = replaceURLWithHTMLLinks(safe_message);
  var safe_from = $('<div/>').text(object.from).html();
  $('<tr><td class="chat_date">'+(new Date).getHours() + ':' + (new Date).getMinutes() + ':' + (new Date).getSeconds()+'</td><td class="chat_from">'+safe_from+'</td><td class="chat_msg">'+safe_message+'</td></tr>').insertBefore('#foot');

    } catch (error) {
      console.log(error);
    }
  };
  sock.onclose = function(event) {
    console.log('close');
    switch (event.code) {
      case 1006: //abnormal closure
        return setTimeout(connect, 1000);
    };
  };

});
$(function() {
  $('#input').keydown(function(e) {
    if (e.keyCode === 13) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      setMaybeNick($('#input').val());
      var sendObj = {
        message: $('#input').val(),
      };

      if (typeof nick === 'string') {
        sendObj.nick = nick;
      };

      sock.send(JSON.stringify(sendObj));
      $('#input').val('');
      return;
    }
  });

});
