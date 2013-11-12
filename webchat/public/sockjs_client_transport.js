
function make_sockjs_client_transport (sock) {
  var transport = {}

  sock.onmessage = function (data) {
    console.log('sockjs parse', data)
    try {
      var message = JSON.parse(data.data)
    } catch (error) {
      return console.log('error', error)
    }
    transport.onmessage(message)
  }

  transport.send = function (message) {
    try {
      var data = JSON.stringify(message)
    } catch (error) {
      return console.log('sockjs transport send error:', error)
    }
    sock.send(data)
  }

  return transport
}


