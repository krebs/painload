#!/usr/bin/env python2

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('snmp_exchange')

import pika
import json,argparse,hashlib,sys,time
from snmp_users import snmp_users

SNMP_EXCHANGE='snmp_src'
PROTO_VERSION='1'

parser = argparse.ArgumentParser(description='Generates a list of mac-addresses currently in the network via snmp ')
parser.add_argument('--host',default='141.31.8.11',      help='AMQP host ip address')
parser.add_argument('--port',type=int,default=5672,      help='AMQP host port')
parser.add_argument('-u','--username',default='guest',   help='AMQP username') 
parser.add_argument('-p','--password',default='guest',   help='AMQP password') 
parser.add_argument('-r','--repeat',type=int,default=20, help='SNMP_Polling Delay') 
parser.add_argument('--unique-key',action='store_true',   help='Unique Key') 
args = parser.parse_args()
if args.unique_key:
    print hashlib.sha1(PROTO_VERSION+args.host+str(args.port)).hexdigest()
    sys.exit(0)

args = parser.parse_args()

connection = pika.AsyncoreConnection(pika.ConnectionParameters(
          credentials = pika.PlainCredentials(args.username,args.password), 
          host=args.host,port=args.port))
channel = connection.channel()

channel.exchange_declare(exchange=SNMP_EXCHANGE,
                             type='fanout')

log.info('Starting up snmp_users')
s = snmp_users()
print ' Sending Messages in Intervals. To exit press CTRL+C'
while True:
  log.info("collecting data from network")
  ret = s.collect()
  data = { 'type' : 'snmp', 'subtype' : 0, 'data' : ret}
  log.debug("writing data to queue : %s" % data)
  channel.basic_publish(exchange=SNMP_EXCHANGE,
      routing_key='',
      body=json.dumps(data))
  time.sleep(args.repeat)
