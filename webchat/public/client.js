var settings = {}

$(function updateTime () {
  $('#time').html(getCurTime());
  setTimeout(updateTime,'1000');
  return true;
});

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
      clientParser(object);

    } catch (error) {
      console.log(error);
      throw error;
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
      var input = ($('#input').val());
      $('#input').val('');

      var command = inputParser(input)
      return (commands[command.method] || commands.badcommand)(settings, command.params)
    }
  });

});
