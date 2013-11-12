try {
  module.exports = RPC
}
catch(e){
}

function RPC (transport) {
  this._id = 0
  this._waiting_callbacks = {}
  this._methods = {}
  this._transport = transport

  transport.onmessage = this.onmessage.bind(this)
}

RPC.prototype.register = function (method, params, callback) {
  this._methods[method] = callback
}

RPC.prototype.send = function (method, params, callback) {
  var message = {
    method: method,
    params: params,
  }
  if (callback) {
    var id = ++this._id
    this._waiting_callbacks[id] = callback
    message.id = id
  }
  return this._transport.send(message)
}

function _is_request (message) {
  return typeof message.method === 'string'
}

function _is_response (message) {
  return message.hasOwnProperty('result')
      || message.hasOwnProperty('error')
}

RPC.prototype.onmessage = function (message) {
  console.log('RPC message:', message)
  if (_is_request(message)) {
    return this._on_request(message)
  }
  if (_is_response(message)) {
    return this._on_response(message)
  }
  return this._on_bad_message(message)
}

RPC.prototype._on_request = function (request) {
  var method = this._methods[request.method] || function(){
    console.log('method not found', request.method)
  }
  var params = request.params
  var id = request.id

  var transport = this._transport

  if (typeof id === 'string' || typeof id === 'number' || id === null) {
    return method(params, function (error, result) {
      var response = {
        id: id,
      }
      if (error) {
        response.error = error
      } else {
        response.result = result
      }
      console.log('request:', request, '->', response)
      return transport.send(response)
    })
  } else {
    return method(params, function (error, result) {
      var response = {
        id: id,
      }
      if (error) {
        response.error = error
      } else {
        response.result = result
      }
      console.log('notification:', request, '->', response)
    })
  }
}

RPC.prototype._on_response = function (response) {
  var result = response.result
  var error = response.error
  var id = response.id

  var callback = this._waiting_callbacks[id]
  delete this._waiting_callbacks[id]

  return callback(result, error)
}
