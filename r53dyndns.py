#! /usr/bin/env python3

"""Updates a Route53 hosted A record with the current ip of the system.
"""

import argparse
import logging
import dns
import dns.resolver
import socket
import boto3

def get_current_ip():
    resolver = dns.resolver.Resolver()
    resolver.nameservers=[socket.gethostbyname('resolver1.opendns.com')]

    for rdata in resolver.resolve('myip.opendns.com', 'A') :
        current_ip = str(rdata)

    logging.info(f'Current IP address: {current_ip}')

    return current_ip


def get_zone(zone_to_update):
    client = boto3.client('route53')
    zone = client.list_hosted_zones_by_name(
        DNSName=zone_to_update,
        MaxItems='1'
    )

    hosted_zone = zone['HostedZones']

    for z in hosted_zone:
        hosted_zone_id = z['Id'].split('/')[2]

    logging.info(f'Hosted Zone ID: {hosted_zone_id}')

    return hosted_zone_id


def get_record_ip(hosted_zone_id, record_to_update):
    client = boto3.client('route53')
    record_set = client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        StartRecordName=record_to_update,
        StartRecordType='A',
        MaxItems='1'
    )

    record = record_set['ResourceRecordSets']

    for v in record:
        record_ip = v['ResourceRecords'][0]['Value']

    logging.info(f'Current record IP Address: {record_ip}')

    return record_ip


def update_record(hosted_zone_id, record_to_update, current_ip):

    def get_change_status(change_id):
        client = boto3.client('route53')
        change_status = client.get_change(
            Id=change_id
        )

        status = change_status['ChangeInfo']['Status']

        logging.info(f'Change Status: {status}')

        return status


    client = boto3.client('route53')
    change = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Comment': 'Updated by r53dns.py',
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': record_to_update,
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [
                            {
                                'Value': current_ip
                            }
                        ]
                    }
                }
            ]
        }
    )

    change_id = change['ChangeInfo']['Id'].split('/')[2]
    logging.info(f'Change ID: {change_id}')

    status = status = get_change_status(change_id)

    if status == 'PENDING':
        logging.info('Waiting for change to complete...')

    while status == 'PENDING':
        status = get_change_status(change_id)

    if status == 'INSYNC':
        logging.info('Change complete')

    return status


def main():
    parser = argparse.ArgumentParser(description='Update a Route53 hosted A record with with current external IP address of the system.')
    parser.add_argument('-r', '--record', help='specify the DNS A record to update')
    parser.add_argument('-v', '--verbose', help='enable verbose output',
                        action="store_true")
    args = parser.parse_args()

    if args.record is None:
        logging.error('No record specified')
        parser.print_help()
        exit(-1)

    if args.verbose:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(message)s',
        )
        logging.info('Verbose output enabled')

    record_to_update = args.record
    logging.info(f'Updating A record: {record_to_update}')

    zone_to_update = '.'.join(record_to_update.split('.')[-2:])
    logging.info(f'Route53 zone: {zone_to_update}')

    current_ip = get_current_ip()
    hosted_zone_id = get_zone(zone_to_update)
    record_ip = get_record_ip(hosted_zone_id, record_to_update)

    if current_ip == record_ip:
        logging.info('IP addresses match - nothing to do')
        exit(0)

    status = update_record(hosted_zone_id, record_to_update, current_ip)

    if status == 'INSYNC':
        logging.info(f'Updated A record {record_to_update} in hosted zone {zone_to_update} ({hosted_zone_id}) from {record_ip} to {current_ip}')


if __name__ == '__main__':
    main()
