var http = require('http');
var slurp = require('./slurp');

var options = {
  host: 'scexchange.bitparking.com',
  port: 8080,
  path: '/api/t2'
};

var last_id = 0;
var last_price = 0;
function t2 () {
  http.get(options, function(res) {
    slurp(res, function (data) {
      try {
        data = JSON.parse(data);
      } catch (exn) {
        return console.error('[1;31m' + exn.stack + '[m');
      };
      data
        .sort(function (a, b) {
          return a.id - b.id;
        })
        .forEach(function (x) {
          if (x.id > last_id) {
            last_id = x.id;

            x.date = new Date(Number(x.date) * 1000);

            var price = x.price.toString();
            while (price.length < 'x.xxxxxxxx'.length) {
              price += 0;
            }
            if (x.price > last_price) {
              price = '[32m' + price + '[m'
            }
            if (x.price < last_price) {
              price = '[31m' + price + '[m'
            }
            last_price = x.price;

            var c = ({ buy: '[32m', sell: '[31m' })[x.type];
            var m = '';
            m += x.id
            m += ' ' + JSON.parse(JSON.stringify(x.date))
            m += ' ' + price
            m += ' ' + c + x.amount + '[m'
            console.log(m);

          };
        });
    });
  }).on('error', function(e) {
    console.log("Got error: " + e.message);
  });
};

setInterval(t2, 1000);
