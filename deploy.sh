#!/usr/bin/env bash

BUILD=$1
docker pull icoqu/secretshare:$1
docker stop secretshare
docker rm secretshare
docker run -d --restart unless-stopped\
     --name secretshare \
     -p 127.0.0.1:8000:5000 \
     -e SECRET_KEY=$SECRET_KEY \
     --link redis:redis \
     -e REDIS_HOST=redis \
     -e REDIS_PORT=6379 \
     icoqu/secretshare:nightly
docker tag icoqu/secretshare:$1 icoqu/secretshare:current


docker pull redis:latest
docker stop redis
docker rm redis
docker run -d --restart unless-stopped \
     --name redis \
     -p 127.0.0.1:6379:6379 \
     -v /etc/redis/:/data \
     redis redis-server /data
docker tag redis:latest redis:current