# gozerbot/xmpp/namespace.py
#
#

## CONSTANTS

attributes = {}
subelements = {}

attributes['message'] = ['type', 'from', 'to', 'id']
subelements['message'] = ['subject', 'body', 'error', 'thread', 'x']

attributes['presence'] = ['type', 'from', 'to', 'id']
subelements['presence'] = ['show', 'status', 'priority', 'x']


attributes['iq'] = ['type', 'from', 'to', 'id']
subelements['iq'] = ['query', 'error']
