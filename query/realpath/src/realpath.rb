#!/usr/bin/env ruby

begin
  $stdout.print File.realpath(ARGV[0])
  $stdout.print "\n"
rescue Exception => err
  $stderr.print err
  $stderr.print "\n"
  exit 1
end
