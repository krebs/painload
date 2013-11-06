# ship - shellscript installation processor

  This utility is used to build modular shell scripts using recursive macro
  expansion.

## Quickstart Guide

    BUILD_PATH=libs ./build compile INPUTFILE OUTPUTFILE

  If this doesen make science to you, then prepend `debug=true` to get all
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
