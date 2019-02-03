#!/usr/bin/env bash

TAG=1.1.0
IMAGE=bradqwood/route53-dyndns

docker build -t $IMAGE:$TAG .
docker tag $IMAGE:$TAG $IMAGE:latest
docker push $IMAGE:$TAG
docker push $IMAGE:latest
