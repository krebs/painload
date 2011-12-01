#!/bin/sh
HERE=$(dirname $(readlink -f $0))
ln -snf $HERE/hooks/pre-commit $HERE/../db/.git/hooks/pre-commit
