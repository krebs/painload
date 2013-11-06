# ship - shellscript installation processor

  This utility is used to build modular shell scripts using recursive macro
  expansion.

## Quickstart Guide

    BUILD_PATH=libs ./build compile INPUTFILE OUTPUTFILE

  If this doesn't make science to you, then prepend `debug=true` to get all
  the intermediate files printed to stdout.

## Make Interface

  Put libraries into `lib`.
  Put executables into `src`.

  Build all executables from `src` into `tmp` with

    make [all]

  Build all executables from `src` into `tmp` and `//bin` with

    make install

  Undo `make [all]` with

    make clean

  Undo `make install` with

    make distclean

## Macro Development

  To define a new macro, you have to add a function like

    ## usage: BRE -> FUNCTION_NAME \1 [\2 ...]

  where `BRE` is a basic regular expression, that has to match a whole
  line.  `FUNCTION_NAME` should be the name of a function that outputs
  a `sed` script.  `\1` refers to the line number, where the macro is
  used and `\2 ...` are the backreferences into `BRE`.  E.g.

    ## usage: #@date \([.*]\) -> build_datemacro \1 \2
    build_datemacro() {
      printf '%da\\\n%s\n' "$1" "$(date +"$2")"
    }

  Like in this example, the line number `\1`, which gets mapped to `$1`,
  is usually used to only change the line, where the macro got called.
  The second argument gets passed as format specifier to `date`.

  Further examples can be found in `./build`.
