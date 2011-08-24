#!/bin/sh
dirname=`dirname  $(readlink -f $0)`
$dirname/mtgox.ticker | python $dirname/json_ticker_helper.py
