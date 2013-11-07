module.exports = {
  create_beeper: create_beeper,
}

var child_process = require('child_process');

function create_beeper (spec) {
  return {
    beep: beep,
  }
  function beep (freq, len) {
    var child = child_process.spawn('beep', [
        '-f', freq,
        '-l', len,
    ]);
    child.stdout.on('data', function (data) {
      console.log('stdout: ' + data);
    });

    child.stderr.on('data', function (data) {
      console.log('stderr: ' + data);
    });

    child.on('close', function (code) {
      if (code !== 0) {
        console.log('child process exited with code ' + code);
      }
    });
  }
}
