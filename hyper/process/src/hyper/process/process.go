package hyper

import "fmt"
import "http"
import "bytes"
import "json"
import "os"

type Process struct {
  Path string               `json:"path"`
  Argv []string             `json:"argv"`
  Envp map[string]string    `json:"envp"`
  //Stdin string              `json:"stdin"`
  Stdout string             `json:"stdout"`
  Stderr string             `json:"stderr"`
  process *os.Process
  process_stdin *os.File
  process_stdout *os.File
  process_stderr *os.File
  id string
}

func (p *Process) Id() string {
  return p.id
}

func NewProcess(req *http.Request) (*Process, os.Error) {
  body := make([]byte, 4096)
  _, err := req.Body.Read(body)
  if err != nil {
    return nil, err
  }

  body = bytes.TrimRight(body, string([]byte{0}))

  var p Process

  if err := json.Unmarshal(body, &p); err != nil {
    return nil, err
  }

  p.id = gensym()

  if err := p.Start(); err != nil {
    return nil, err
  }

  return &p, nil
}

func (hp *Process) Write(b []byte) {
  n, err := hp.process_stdin.Write(b)
  if err != nil {
    fmt.Printf("Write: %s\n", err)
  } else {
    fmt.Printf("Wrote: %d bytes\n", n)
  }
}

func (hp *Process) Start() os.Error {
  var name = hp.Path //os.Args[1] //"/usr/b"
  var argv = hp.Argv //os.Args[1:] //[]string{ "bc" }
  //var chroot = false
  //var dir = "/var/empty"
  var files [3][2]*os.File
  var err os.Error

  for i, _ := range files {
    files[i][0], files[i][1], err = os.Pipe()
    if err != nil {
      return err
    }
  }

  var env []string
  for k, v := range hp.Envp {
    env = append(env, fmt.Sprintf("%s=%s", k, v))
  }

  var attr = &os.ProcAttr{
    //Dir: dir,
    Env: env, //os.Environ(),
    Files: []*os.File{ files[0][0], files[1][1], files[2][1]},
  }

  //var foo, _ = json.Marshal(attr)
  //fmt.Printf("%s\n", foo)

  hp.process, err = os.StartProcess(name, argv, attr)
  if err != nil {
    return err
  }

  hp.process_stdin = files[0][1]
  hp.process_stdout = files[1][0]
  hp.process_stderr = files[2][0]

  for _, file := range attr.Files {
    file.Close()
  }

  go reader(hp.process_stdout)
  go reader(hp.process_stderr)
  return nil
}

func reader(file *os.File) {
  var b []byte = make([]byte, 1024)
  var err os.Error = nil
  for err == nil {
    var n int
    n, err = file.Read(b)
    fmt.Printf("data: %d, %s\n", n, b)
  }
}

func gensym() string {
  f, _ := os.Open("/dev/urandom") 
  b := make([]byte, 16) 
  f.Read(b) 
  f.Close() 
  uuid := fmt.Sprintf("%x-%x-%x-%x-%x", b[0:4], b[4:6], b[6:8], b[8:10], b[10:]) 
  return uuid
}

