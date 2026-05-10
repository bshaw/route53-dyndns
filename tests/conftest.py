import boto3
import pytest
from moto import mock_aws

ZONE = 'example.com'
RECORD = 'home.example.com'
OLD_IP = '1.1.1.1'
NEW_IP = '2.2.2.2'


@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'testing')
    monkeypatch.setenv('AWS_DEFAULT_REGION', 'us-east-1')


@pytest.fixture
def route53():
    with mock_aws():
        yield boto3.client('route53')


@pytest.fixture
def zone_id(route53):
    zone = route53.create_hosted_zone(Name=ZONE, CallerReference='ref')
    return zone['HostedZone']['Id'].split('/')[2]


@pytest.fixture
def seeded_record(route53, zone_id):
    route53.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Changes': [{
                'Action': 'CREATE',
                'ResourceRecordSet': {
                    'Name': RECORD,
                    'Type': 'A',
                    'TTL': 60,
                    'ResourceRecords': [{'Value': OLD_IP}],
                },
            }],
        },
    )
    return zone_id
