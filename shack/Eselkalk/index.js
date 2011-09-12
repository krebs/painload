//
// node //shack/Eselkalk DATE
//
// where DATE ∈ [YYYY[-MM]], defaulting to the current YYYY-MM
//

range = process.argv[2] ||
    JSON.parse(JSON.stringify(new Date())).slice(0, '....-..'.length)

function dates(date) {
  var year = date.getFullYear()
  var month = date.getMonth()

  var i = new Date([year, (month < 9 ? '0' : '') + (month + 1)].join('-'))

  var days = []
  var next_day = 4;
  for (
      ; i.getMonth() === month
      ; i = new Date(+i + 24 * 60 * 60 * 1000)) {
    if (i.getDay() === next_day) {
      next_day = next_day === 3 ? 4 : 3
      if (next_day === 3) {
        var next_4day = new Date(+i + 7 * 24 * 60 * 60 * 1000)
        if (next_4day.getMonth() !== month) {
          i = new Date(+i - 24 * 60 * 60 * 1000)
          next_4day = 4
        }
      }
      days.push(new Date(+i + (20 * 60 + i.getTimezoneOffset()) * 60 * 1000))
      while (i.getDay() !== 0) {
        i = new Date(+i + 24 * 60 * 60 * 1000)
      }
    }
  }

  return days
}


result = []

// TODO if (/^....-..-..$/.test(range)) { ... }
if (/^....-..$/.test(range)) {
  result = dates(new Date(range))
}
else if (/^....$/.test(range)) {
  ['01','02','03','04','05','06','07','08','09','10','11','12'
  ].forEach(function (i) {
    result = result.concat(dates(new Date([range, i].join('-'))))
  })
}
else {
  throw new Error('You are made of stupid! ' + range)
}

console.log(JSON.stringify(result, null, 2))
