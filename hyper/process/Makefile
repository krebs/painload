include $(GOROOT)/src/Make.inc

GCIMPORTS = -I pkg/$(GOOS)_$(GOARCH)
LDIMPORTS = -L pkg/$(GOOS)_$(GOARCH)

TARG=main
GOFILES=\
	main.go\

include $(GOROOT)/src/Make.cmd

export GOPATH := $(PWD)
.PHONY: prepare
prepare:
	#goinstall -v github.com/garyburd/twister/server
	goinstall -v gorilla.googlecode.com/hg/gorilla/mux
	goinstall -v $(PWD)/src/hyper/process

_go_.$O: prepare
