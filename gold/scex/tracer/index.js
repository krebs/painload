#! /usr/bin/env node
//
// usage: [idle_mark=N] tracer
//
// Where the optional idle_mark tells the tracer to output idle marks every N
// seconds.
//
var http = require('http');
var slurp = require('./slurp');

var options = {
  host: 'scexchange.bitparking.com',
  port: 8080,
  path: '/api/t2'
};

var interval = 1000;
var idle_mark = Number(process.env.idle_mark) * interval;

var last_id = 0;
var last_price = 0;
var last_output = new Date(0);
function t2 () {
  var now = new Date()
  http.get(options, function(res) {
    slurp(res, function (data) {
      try {
        data = JSON.parse(data);
      } catch (exn) {
        return console.error('[1;31m' + exn.stack + '[m');
      };
      data = data.sort(function (a, b) {
        return a.id - b.id;
      }).filter(function (x) {
        return x.id > last_id;
      });
      if (data.length > 0) {
        data.forEach(function (x) {
          last_id = x.id;

          x.date = new Date(Number(x.date) * 1000);

          var price = render_price(x.price, last_price);
          last_price = x.price;

          var c = ({ buy: '[32m', sell: '[31m' })[x.type];
          var m = '';
          m += x.id
          m += ' ' + JSON.parse(JSON.stringify(x.date))
          m += ' ' + price
          m += ' ' + c + x.amount + '[m'
          console.log(m);
          last_output = now;
        });
      } else {
        if (idle_mark) {
          if (now - last_output >= idle_mark) {
            var price = render_price(last_price);
            var m = last_id
            m += ' ' + JSON.parse(JSON.stringify(now));
            m += ' ' + price
            console.log(m);
            last_output = now;
          };
        };
      };
    });
  }).on('error', function(e) {
    console.log("Got error: " + e.message);
  });
};

function render_price(price, last_price) {
  var rendered_price = price.toString();
  while (rendered_price.length < 'x.xxxxxxxx'.length) {
    rendered_price += 0;
  };
  if (last_price) {
    if (price > last_price) {
      rendered_price = '[32m' + rendered_price + '[m'
    };
    if (price < last_price) {
      rendered_price = '[31m' + rendered_price + '[m'
    };
  };
  return rendered_price;
};

setInterval(t2, interval);
