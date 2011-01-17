#!/usr/bin/env python2
import pika
import json,argparse
from snmp_users import snmp_users
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('snmp_exchange')

SNMP_EXCHANGE='snmp_src'

parser = argparse.ArgumentParser(description='generates dummy package on given exchange against AMQP')
parser.add_argument('--host',default='141.31.8.11',      help='AMQP host ip address')
parser.add_argument('--port',type=int,default=5672,      help='AMQP host port')
parser.add_argument('-u','--username',default='guest',   help='AMQP username') 
parser.add_argument('-p','--password',default='guest',   help='AMQP password') 
parser.add_argument('-r','--repeat',type=int,default=20, help='SNMP_Polling Delay') 
args = parser.parse_args()

connection = pika.AsyncoreConnection(pika.ConnectionParameters(
          credentials = pika.PlainCredentials(args.username,args.password), 
          host=args.host,port=args.port))
channel = connection.channel()

channel.exchange_declare(exchange=SNMP_EXCHANGE,
                             type='fanout')

log.info('Starting StatsForUser Module (mongodb)')
s = snmp_users()
print ' [*] Sending Messages in Intervals. To exit press CTRL+C'
while True:
  log.info("collecting data from network")
  ret = s.collect()
  data = { 'type' : 'snmp', 'subtype' : 0, 'data' : ret}
  log.debug("writing data to queue : %s" % data)
  channel.basic_publish(exchange=SNMP_EXCHANGE,
      routing_key='',
      body=json.dumps(data))
