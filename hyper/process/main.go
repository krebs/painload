package main

import "fmt"
import "os"


func reader(file *os.File) {
  var b []byte = make([]byte, 1024)
  var err os.Error = nil
  for err == nil {
    var n int
    n, err = file.Read(b)
    fmt.Printf("data: %d, %s\n", n, b)
  }
}

func main() {
  var name = "/usr/bin/bc"
  var argv = []string{ "bc" }
  var envv = []string{ "FOO=23" }
  //var chroot = false
  var dir = "/var/empty"
  var files [3][2]*os.File
  var err os.Error
 
  for i, _ := range files {
    files[i][0], files[i][1], err = os.Pipe()
    err = err
  }

  var attr = &os.ProcAttr{
    Dir: dir,
    Env: envv,
    Files: []*os.File{ /*files[0][0] */ os.Stdin, files[1][1], files[2][1]},
  }

  var p *os.Process

  p, err = os.StartProcess(name, argv, attr)

  for _, file := range attr.Files {
    file.Close()
  }

  p=p

  go reader(files[1][0])
  reader(files[2][0])

  fmt.Printf("hello, world\n")

}
