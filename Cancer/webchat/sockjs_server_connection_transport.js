
module.exports = function make_sockjs_server_connection_transport (connection) {
  var transport = {}

  connection.on('data', function (data) {
    try {
      var message = JSON.parse(data)
    } catch (error) {
      return console.log('error', error)
    }
    transport.onmessage(message)
  })
  connection.on('close', function () {
  })

  transport.send = function (message) {
    try {
      var data = JSON.stringify(message)
    } catch (error) {
      return console.log('sockjs transport send error:', error)
    }
    connection.write(data)
  }

  return transport
}
