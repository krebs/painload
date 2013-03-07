function slurp (stream, callback) {
  var data = []
  stream.on('data', function (chunk) {
    data.push(chunk)
  })
  stream.on('end', function () {
    callback(null, Buffer.concat(data))
  })
  stream.resume()
}


var path = require('path')
var city_dat = path.join(__dirname, 'GeoLiteCity.dat')

var geoip = require('geoip')
var city = new geoip.City(city_dat)

slurp(process.stdin, function (err, data) {
  var lines = data.toString().split('\n')
  // remove last, empty element (caused by the [mandatory] final \n)
  if (lines.length > 1 && lines[lines.length - 1] === '') {
    lines.pop()
  }
  var name = 0, addr = 1
  lines
    .map(function (line) { return line.split(' ') })
    .forEach(function (host) {
      //city.lookup(host[addr], function (err, loc) {
      //  if (err) {
      //    console.error('#', host[name], err.message)
      //  } else {
      //    console.log(host[name] + ': ' + loc.longitude + ',' + loc.latitude)
      //  }
      //})
      var loc = city.lookupSync(host[addr])
      //if (!loc) { console.error('#', host[name]) }
      if (loc) {
        var a = loc.latitude
        var b = loc.longitude
        //var c = loc.altitude
        //var geo = 'geo:' + [a,b,c].join(',')
        var geo = 'geo:' + [a,b].join(',')

        console.log(host[name], geo)
      }
    })
})
