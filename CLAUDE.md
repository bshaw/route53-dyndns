# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-script Python tool (`r53dyndns.py`) that updates a Route53 A record with the machine's current external IP. It's designed to run as a one-shot process — invoked via cron, Kubernetes CronJob, or Docker — not as a long-running daemon.

## Running locally

```bash
pip3 install -r requirements.txt
python3 r53dyndns.py --record example.com --verbose
```

AWS credentials are picked up via boto3's standard chain (env vars, `~/.aws/credentials`, IAM role, etc.).

## Building the Docker image

```bash
docker build -t route53-dyndns .
docker run --rm -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... route53-dyndns --record example.com --verbose
```

The CI workflow (`build-and-push.yml`) builds and pushes multi-arch images (`amd64`, `arm64`, `arm/v7`) to Docker Hub on every push to `master`, weekly on Sundays, and on `workflow_dispatch`.

## Architecture

All logic lives in `r53dyndns.py`. The flow is:

1. **Get current IP** — DNS query to `myip.opendns.com` via OpenDNS resolver (faster/more reliable than HTTP-based IP lookup services).
2. **Get hosted zone ID** — `list_hosted_zones_by_name` for the apex domain extracted from `--record`.
3. **Get current record IP** — `list_resource_record_sets` for the A record.
4. **Compare and UPSERT** — if IPs differ, calls `change_resource_record_sets` with `UPSERT` action and polls until status is `INSYNC`.

The script exits 0 when IPs already match (no-op) or after a successful update, and exits non-zero on errors.

## Deployment patterns

- **Kubernetes CronJob**: recommended for cluster environments; see README for manifest example.
- **Docker / cron**: `docker run --rm` invocation scheduled via crontab.
- **docker-compose**: provided but note `restart: always` runs it continuously — prefer the cron approach for new deployments.
