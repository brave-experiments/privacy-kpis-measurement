#!/bin/bash
docker build . -t kaytwo/privacykpis:base && for b in chrome firefox brave ; do docker build -f Dockerfile.$b . -t kaytwo/privacykpis:$b ; done