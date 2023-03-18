# Amazon Route53 Dynamic DNS

A simple dynamic DNS service for Route53.

## Requirements

* Python3 (Tested on 3.11.2)
* [Boto3](https://github.com/boto/boto3)
* [dnspython](https://github.com/rthalley/dnspython)

## Usage

## Docker

```bash
docker run -d \
    --name route53 \
    -e AWS_ACCESS_KEY_ID= \
    -e AWS_SECRET_ACCESS_KEY= \
    -e ROUTE53_DOMAIN_A_RECORD= \
    -e ROUTE53_UPDATE_FREQUENCY=10800 \
    bshaw/route53-dyndns
```

## Command line

```bash
python3 r53dyndns.py --help
usage: r53dyndns.py [-h] [-r RECORD] [-v]

Update a Route53 hosted A record with with current external IP address of the system.

optional arguments:
  -h, --help            show this help message and exit
  -r RECORD, --record RECORD
                        specify the DNS A record to update
  -v, --verbose         enable verbose output

```

## Required Environment Variables

* `AWS_ACCESS_KEY_ID` - An AWS Access Key
* `AWS_SECRET_ACCESS_KEY` - An AWS Secret Key
* `ROUTE53_DOMAIN_A_RECORD` - The A record to update, such as myhouse.domain.com
* `ROUTE53_UPDATE_FREQUENCY` - The frequency (in seconds) to check for updates. Unless you have very specific needs, consider using a very large value here.

## Credentials

Boto supports multiple ways to supply credentials.

* When running locally / via the command line, it's easy to rely on a [shared credentials file](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file)
* When using Docker, it is recommended to use [environment variables](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#environment-variable-configuration)

See the official documentation for more details:
[https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.htm](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.htm)

## Retrieving your external IP

This service performs a DNS query to retrieve your IP address from an OpenDNS resolver. This method arguably faster and more reliable than using an http(s) service.

Similar functionality could be done via the shell using dig: `dig +short myip.opendns.com @resolver1.opendns.com;`
