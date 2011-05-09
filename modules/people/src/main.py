#!/usr/bin/env python2
import sys,json,time
from snmp_users import snmp_users
import logging
import genericore as gen
MODULE_NAME='snmp_users'
log = logging.getLogger(MODULE_NAME)
PROTO_VERSION = 1
DESCRIPTION = 'performes statistical analysis against mails from stream'


# set up instances of needed modules
conf = gen.Configurator(PROTO_VERSION,DESCRIPTION)  
amqp = gen.auto_amqp(MODULE_NAME)   
s = snmp_users(MODULE_NAME)       # the magic mail parsing class

conf.configure([amqp,s]) #set up parser and eval parsed stuff

# start network connections
amqp.create_connection()

log.info('Starting up snmp_users')
print ' Sending Messages in Intervals. To exit press CTRL+C'
try:
  while True:
    log.info("collecting data from network")
    ret = s.collect()
    data = { 'type' : 'snmp', 'subtype' : 0, 'data' : ret}
    log.debug("writing data to queue : %s" % data)
    amqp.publish(json.dumps(data))
    time.sleep(s.repeat)
except Exception as e:
  print "something happened :( " + str(e)
