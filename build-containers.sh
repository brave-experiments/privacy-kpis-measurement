#!/bin/bash
docker build . -t kaytwo/privacykpis:base && \
for b in chrome firefox brave chrome-ubo
do 
  docker build -f Dockerfile.$b . -t kaytwo/privacykpis:$b
done
