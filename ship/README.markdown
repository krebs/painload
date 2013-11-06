# ship - shellscript installation processor

  This utility is used to build modular shell scripts using recursive macro
  expansion.

## Quickstart Guide

    BUILD_PATH=libs ./build compile INPUTFILE OUTPUTFILE

  If this doesen make science to you, then prepend `debug=true` to get all
  the intermediate files printed to stdout.

## Make Interface

  Build all executables from `src/` into `tmp/`:

    make [all]

  Build all executables into `tmp/` and `//bin/`:

    make install

  Undo `make [all]`:

    make clean

  Undo `make install`:

    make distclean
