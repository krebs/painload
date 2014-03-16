var IRC = require('irc')
var FeedParser = require('feedparser')
var Request = require('request')

var irc_server = 'ire.retiolum'
var master_nick = 'knews'
var news_channel = '&testing'
var feeds_file = 'new_feeds'
var feedbot_loop_delay = 60 * 1000 // [ms]

function main () {
  // XXX mangle nick to not clash with newsbot.py
  var master = new IRC.Client(irc_server, master_nick + '_2', {
    channels: [ news_channel ],
  })

  master.on('message' + news_channel, function (nick, text, message) {
    if (is_talking_to(master_nick, text)) {
      var parse = /^[^:]*:\s*(\S*\S)\s*$/.exec(text)
      if (parse) {
        client.say(to, nick + ': ' + parse[1] + '?')
      }
  })

  master.once('registered', function () {
    // read feeds file and create a feedbot for each entry
    require('fs')
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

        // XXX mangle nick to not clash with newsbot.py
        var nick = parts[0] + '_2'
        var uri = parts[1]
        var channels = parts[2].split(' ')

        // XXX mangle channel to not clash with newsbot.py
        channels = channels.map(function (channel) {
          return channel === '#news' ? news_channel : channel
        })

        return create_feedbot(nick, uri, channels)
      })
  })
}

function create_feedbot (nick, uri, channels) {
  var client = new IRC.Client(irc_server, nick, {
    channels: channels,
  })

  // say text in every joined channel
  function broadcast (text) {
    Object.keys(client.chans).forEach(function (channel) {
      client.say(channel, text)
    })
  }
  
  client.once('registered', loop_feedparser)

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

      var indexOfLastTitle = items
        .map(function (x) { return x.title })
        .indexOf(client.lastTitle)

      var newitems = items
      var olditems = []

      // if items contain lastTitle, then only items after that are news
      if (!!~indexOfLastTitle) {
        olditems = newitems.splice(0, indexOfLastTitle + 1)
      }

      if (newitems.length > 0) {
        // only broadcast news if we're not starting up
        // (i.e. we already have a lastTitle)
        if (client.lastTitle) {
          newitems.forEach(function (item) {
            broadcast(item.title + ' ' + item.link)
          })
        }

        client.lastTitle = newitems[newitems.length - 1].title
      }

      return setTimeout(loop_feedparser, feedbot_loop_delay)
    })
  }
}

// return true if text "is talking to" my_nick
function is_talking_to (my_nick, text) {
  return text.slice(0, my_nick.length) === my_nick
      && text[my_nick.length] === ':'
}

if (require.main === module) {
  main()
}
