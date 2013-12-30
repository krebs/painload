


var x = 3000;

var t = 0;
var i = 0;
var j = 0.00001;
var t0 = new Date();
(function rec () {
  
  var t1 = new Date();
  console.error('dt = ' + (t1 - t0));
  t0 = t1;

  if (x === 3000) {
    x = 1000;
  } else {
    x = 3000;
  };

  console.log('2000 50  0 50  2000 50  0 50  ' + x + ' 100  0 0');
  return setTimeout(rec, 1000);

  i += 0.01;
  console.log((2000 + Math.sin(i) * 1000 | 0) + ' 0');
  return setTimeout(rec, 1);

  var f = Math.abs(1000 + 500 * Math.tan( t ));
  var scale = 1;

  console.log(((f * scale)|0) + ' 0');

  t++;
  setTimeout(rec, 100);
  //process.nextTick(rec);
})();
