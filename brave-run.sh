#!/bin/bash

for profilenum in 3 4 ; do
    docker run -d -v privacykpis.profiles.$profilenum:/tmp/profiles --privileged kaytwo/privacykpis:brave -e PYTHONUNBUFFERED=0 --profile-index $profilenum --platform linux/amd64
done 
