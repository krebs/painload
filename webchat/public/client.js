var settings = {}

$(function updateTime () {
  $('#time').html(getCurTime());
  setTimeout(updateTime,'1000');
  return true;
});

var gensym = (function () {
  var i = 0
  return function () {
    return ++i;
  }
})()

settings.waiting_callbacks = {}

function request (settings, method, params, callback) {
  var id = gensym()
  settings.waiting_callbacks[id] = callback
  settings.sock.send({method: method, params: params, id: id});
}

$(function connect() {
  settings.sock = new SockJS('/echo');

  settings.sock.onopen = function() {
    console.log('open');
    request(settings, 'coi', {}, function (error, result) {
      if (error) {
        console.log('coi error', error)
      } else {
        settings.nick = result.nick //TODO: write to display
        settings.addr = result.addr //TODO: write to display
      }
    })
  };
  settings.sock.onmessage = function(e) {
    console.log('message', e.data);
    try {
      var object = JSON.parse(e.data);
      console.log(object);

    } catch (error) {
      console.log(error);
      throw error;
    }
    if (typeof object.method === 'string') {
      return methodDispatcher(settings, object);
    } else if (typeof object.result === 'string') {
      return resultDispatcher(settings, object);
    } else {
      console.log('bad message:', object)
    }
  }
  settings.sock.onclose = function(event) {
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
