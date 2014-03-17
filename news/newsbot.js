var IRC = require('irc')
var FeedParser = require('feedparser')
var Request = require('request')
var Parse = require('shell-quote').parse
var FS = require('fs')
var HTTP = require('http')
var FormData = require('form-data')
var URL = require('url')

var irc_server = 'ire.retiolum'
var master_nick = 'knews'
var news_channel = '#news'
var feeds_file = 'new_feeds'
var feedbot_loop_delay = 60 * 1000 // [ms]
var url_shortener_host = 'go'

var slaves = {}

function main () {
  var master = new IRC.Client(irc_server, master_nick, {
    channels: [ news_channel ],
  })

  master.on('message' + news_channel, function (nick, text, message) {
    if (is_talking_to(master_nick, text)) {
      var request = parse_request(text)
      if (request) {
        return run_command(request.method, request.params, function (error, result) {
          if (error) {
            return master.say(news_channel, '4' + error)
          } else {
            return master.say(news_channel, result)
          }
        })
      }
    }
  })

  master.once('registered', function () {
    // read feeds file and create a feedbot for each entry
    FS
      .readFileSync(feeds_file)
      .toString()
      .split('\n')
      //.filter((function () {
      //  var n = 2;
      //  return function () {
      //    return n-- > 0
      //  }
      //})())
      .filter(function (line) {
        return line.length > 0
      })
      .forEach(function (line) {
        var parts = line.split('|')
        if (parts.length !== 3) {
          console.log('bad new_feeds line ' + lines + ': ' + line)
          return
        }

        var nick = parts[0]
        var uri = parts[1]
        var channels = parts[2].split(' ')

        return create_feedbot(nick, uri, channels)
      })
  })
}

function create_feedbot (nick, uri, channels) {
  var client = new IRC.Client(irc_server, nick, {
    channels: channels,
    autoRejoin: false,
  })

  slaves[nick] = {
    client: client,
    nick: nick,
    uri: uri,
  }

  // say text in every joined channel
  function broadcast (text) {
    Object.keys(client.chans).forEach(function (channel) {
      client.say(channel, text)
    })
  }
  
  client.once('registered', loop_feedparser)
  client.once('registered', deaf_myself)

  client.on('invite', function (channel, from, message) {
    client.join(channel, null)
  })

  client.on('error', function (error) {
    console.log('Error:', error)
  })

  // TODO stopping criteria
  function loop_feedparser () {
    try {
      var request = Request(uri)
      var feedparser = new FeedParser()
    } catch (error) {
      return broadcast('4' + error)
    }

    request.on('error', function (error) {
      broadcast('4request ' + error)
    })
    request.on('response', function (response) {
      if (response.statusCode !== 200) {
        return this.emit('error', new Error('Bad status code'))
      }
      var output = response
      switch (response.headers['content-encoding']) {
        case 'gzip':
          output = zlib.createGunzip()
          response.pipe(output)
          break
        case 'deflate':
          output = zlib.createInflate()
          response.pipe(output)
          break
      }
      this.pipe(feedparser)
    })

    var items = []

    feedparser.on('error', function (error) {
      broadcast('4feedparser ' + error)
    })
    feedparser.on('readable', function () {
      for (var item; item = this.read(); ) {
        items.push(item)
      }
    })
    feedparser.on('end', function () {
      items = items.sort(function (a, b) {
        return a.date - b.date
      })

      var indexOfLastGuid = items
        .map(function (x) { return x.guid })
        .indexOf(client.lastGuid)

      var newitems = items
      var olditems = []

      // if items contain lastGuid, then only items after that are news
      if (!!~indexOfLastGuid) {
        olditems = newitems.splice(0, indexOfLastGuid + 1)
      }

      if (newitems.length > 0) {
        // only broadcast news if we're not starting up
        // (i.e. we already have a lastGuid)
        if (client.lastGuid) {
          newitems.forEach(function (item) {
            return getShortLink(item.link, function (error, shortlink) {
              return broadcast(item.title + ' ' + shortlink)
            })
          })
        }

        client.lastGuid = newitems[newitems.length - 1].guid
      }

      return setTimeout(loop_feedparser, feedbot_loop_delay)
    })
  }
  function deaf_myself () {
    client.send('mode', nick, '+D')
  }
}

// return true if text "is talking to" my_nick
function is_talking_to (my_nick, text) {
  return text.slice(0, my_nick.length) === my_nick
      && text[my_nick.length] === ':'
}

function parse_request (text) {
  var parse = Parse(text)
  return {
    method: parse[1],
    params: parse.slice(2),
  }
}

function run_command (methodname, params, callback) {
  var method = methods[methodname]
  if (method) {
    return method(params, callback)
  } else {
    return callback(new Error('dunno what ' + methodname + ' is'));
  }
}

function getShortLink (link, callback) {
  var form = new FormData()
  form.append('uri', link)

  var request = HTTP.request({
    method: 'post',
    host: url_shortener_host,
    path: '/',
    headers: form.getHeaders(),
  })
  form.pipe(request)

  request.on('response', function (response) {
    var data = ''
    response.on('data', function (chunk) {
      data += chunk
    })
    response.on('end', function () {
      callback(null, data.replace(/\r\n$/,'') + '#' + URL.parse(link).host)
    })
  })
}

var methods = {}
methods.add = function (params, callback) {
  if (slaves.hasOwnProperty(params[0])) {
    return callback(new Error('name already taken'))
  } else {
    create_feedbot(params[0], params[1], [news_channel])
    return callback(null)
  }
}
methods.del = function (params, callback) {
  var nick = params[0]
  if (slaves.hasOwnProperty(nick)) {
    var slave = slaves[nick]
    slave.client.disconnect()
    delete slaves[nick]
    return callback(null)
  } else {
    return callback(new Error('botname not found'))
  }
}
methods.save = function (params, callback) {
  var feeds = Object.keys(slaves)
    .map(function (nick) {
      return slaves[nick]
    })
    .map(function (slave) {
      return [
        slave.nick,
        slave.uri,
        Object.keys(slave.client.chans).join(' '),
      ].join('|')
    }).join('\n') + '\n'
  return FS.writeFile(feeds_file, feeds, function (error) {
    if (error) {
      return callback(error)
    } else {
      return callback(null, 'Feeds saved')
    }
  })
}


if (require.main === module) {
  main()
}
