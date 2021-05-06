#!/bin/bash

docker buildx build . -t kaytwo/privacykpis:base --platform linux/amd64 &&
docker buildx build -f Dockerfile.brave . -t kaytwo/privacykpis:brave --platform linux/amd64
