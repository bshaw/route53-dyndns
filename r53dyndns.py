#! /usr/bin/env python
"""Updates a set of route53-hosted A record(s) with the current ip of the system.
"""
import dns.resolver
import boto.route53
import logging
import os
from optparse import OptionParser
from re import search
import socket
import sys

parser = OptionParser()
parser.add_option('-R', '--record', type='string', dest='records_to_update', help='The A record(s) to update (comma-separated).')
parser.add_option('-v', '--verbose', dest='verbose', default=False, help='Enable Verbose Output.', action='store_true')
(options, args) = parser.parse_args()

if options.records_to_update is None:
    logging.error('Please specify A record(s) with the -R switch.')
    parser.print_help()
    sys.exit(-1)
if options.verbose:
    logging.basicConfig(
        level=logging.INFO,
    )

# get external ip
resolver = dns.resolver.Resolver()
resolver.nameservers = [socket.gethostbyname('resolver1.opendns.com')]
for rdata in resolver.query('myip.opendns.com', 'A'):
    current_ip = str(rdata)
    logging.info('Current IP address: %s', current_ip)

records_to_update = options.records_to_update.split(',')
zone_to_update = '.'.join(records_to_update.split('.')[-2:])

try:
    socket.inet_aton(current_ip)
    conn = boto.route53.connect_to_region(os.getenv('AWS_CONNECTION_REGION', 'us-east-1'))
    zone = conn.get_zone(zone_to_update)
    for record in zone.get_records():
        for record_to_update in records_to_update:
            if search(r'<Record:' + record_to_update, str(record)):
                if current_ip in record.to_print():
                    logging.info('%s IP matches, doing nothing.', record_to_update)
                else:
                    logging.info('%s IP does not match, update needed.', record_to_update)
                    zone.delete_a(record_to_update)
                    zone.add_a(record_to_update, current_ip)
            else:
                logging.info('%s record not found, add needed', record_to_update)
                zone.add_a(record_to_update, current_ip)
except socket.error as e:
     print repr(e)
