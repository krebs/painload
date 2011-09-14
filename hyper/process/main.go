package main

import "json"
import "log"
import "http"
import "gorilla.googlecode.com/hg/gorilla/mux"
import "os"
import "fmt"
import "bytes"

import "hyper/process"

var proc = map[string] *hyper.Process{}

// TODO Retrieve Process, Write, Kill [autokill], get exit code

func RespondJSON(res http.ResponseWriter, v interface{}) os.Error {
  content, err := json.Marshal(v)
  if err == nil {
    log.Printf("< %s", content)
    res.Header().Set("Content-Type", "application/json; charset=\"utf-8\"")
    res.WriteHeader(http.StatusOK)
    res.Write(content)
  } else {
    log.Printf("%s while json.Marshal(%s)", err, v)
  }
  return err
}

func CreateProcessHandler(res http.ResponseWriter, req *http.Request) {
  if p, err := hyper.NewProcess(req); err == nil {
    id := p.Id()
    proc[id] = p
    RespondJSON(res, &map[string]string{
      "path": fmt.Sprintf("/proc/%s", id),
    })
  } else {
    log.Printf("%s", err)
    res.WriteHeader(http.StatusInternalServerError)
  }
}

func RetrieveProcess(res http.ResponseWriter, req *http.Request) {
  if p := proc[mux.Vars(req)["id"]]; p != nil {
    RespondJSON(res, p)
  } else {
    res.WriteHeader(http.StatusNotFound)
  }
}

func FeedProcess(res http.ResponseWriter, req *http.Request) {
  if p := proc[mux.Vars(req)["id"]]; p != nil {
    body := make([]byte, 4096)
    if _, err := req.Body.Read(body); err == nil {
      body = bytes.TrimRight(body, string([]byte{0}))
      p.Write(body)
      //if err := p.Write(body); err == nil {
        RespondJSON(res, true)
      //}
    }
  } else {
    res.WriteHeader(http.StatusNotFound)
  }
}

func main() {

  // Gorilla
  mux.HandleFunc("/proc", CreateProcessHandler).Methods("POST")
  mux.HandleFunc("/proc/{id}", RetrieveProcess).Methods("GET")
  mux.HandleFunc("/proc/{id}", FeedProcess).Methods("POST")

  err := http.ListenAndServe("0.0.0.0:8888", mux.DefaultRouter)
  if err != nil {
    log.Fatal("ListenAndServe: ", err.String())
  }
}
