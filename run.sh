#!/bin/sh

while :
do
  /usr/local/bin/r53dyndns.py -v -R $ROUTE53_DOMAIN_A_RECORD
  echo "Sleeping for $ROUTE53_UPDATE_FREQUENCY seconds..."
  sleep $ROUTE53_UPDATE_FREQUENCY
done
