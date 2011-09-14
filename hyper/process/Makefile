
A := 8

.PHONY: all clean
all: main

clean:
	rm -f main *.$A

%.$A: %.go
	$Ag $<

%: %.$A
	$Al -o $@ $<
