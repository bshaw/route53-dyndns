# Amazon Route53 Dynamic DNS

A simple dynamic DNS service for Route53.

| :warning: WARNING          |
|:---------------------------|
| The latest version no longer keeps the container running with a sleep script.</br> You should either run on a schedule via cron or as a Kubernetes CronJob.</br> If you want to continue using this the old way, please use the `:3` or `3.0.1` tag.
|

## Requirements

* Python3 (Tested on 3.11.2)
* [Boto3](https://github.com/boto/boto3)
* [dnspython](https://github.com/rthalley/dnspython)

## Usage

### Kubernetes - CronJob

#### Secret

Create a secret containing multiple key-value pairs to store your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

```bash
kubectl create secret generic aws-secret --from-literal=AWS_ACCESS_KEY_ID='my_access_-_key_id' --from-literal=AWS_SECRET_ACCESS_KEY='my_secret_access_key'
```

#### CronJob

Run every 5 minutes for the domain `example.com`, using the values from the secret created above.
Make sure to set the record to update in the `args` section.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: route53-dyndns-cron
spec:
  schedule: "*/5 * * * * "
  jobTemplate:
    spec:
      ttlSecondsAfterFinished: 100
      template:
        spec:
          containers:
          - image: docker.io/bshaw/route53-dyndns
            name: route53-dyndns
            imagePullPolicy: Always
            envFrom:
            - secretRef:
                name: route53-dyndns-secret
            args:
            - --record
            - example.com
            - --verbose
          restartPolicy: OnFailure
```

### Docker / Podman

Run once for the domain `example.com`.
Make sure to set values for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and the record to update.

```bash
docker run \
    --rm \
    --name route53 \
    -e AWS_ACCESS_KEY_ID= \
    -e AWS_SECRET_ACCESS_KEY= \
    bshaw/route53-dyndns \
    --record example.com --verbose
```

### Cron

Add to your crontab / scheduler.

Run every 5 minutes for the domain `example.com`.
Make sure to set values for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and the record to update.

```plaintext
*/5 * * * *  docker run --rm --name route53 -e AWS_ACCESS_KEY_ID="access_key_id" -e AWS_SECRET_ACCESS_KEY="secret_access_key" bshaw/route53-dyndns --record example.com --verbose
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

## Credentials

Boto supports multiple ways to supply credentials.

* When running locally / via the command line, it's easy to rely on a [shared credentials file](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#shared-credentials-file)
* When using Docker, it is recommended to use [environment variables](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#environment-variable-configuration)

See the official documentation for more details:
[https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.htm](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.htm)

## Retrieving your external IP

This service performs a DNS query to retrieve your IP address from an OpenDNS resolver. This method arguably faster and more reliable than using an http(s) service.

Similar functionality could be done via the shell using dig: `dig +short myip.opendns.com @resolver1.opendns.com;`
