#!/bin/bash

for profilenum in 3 4 ; do
    for browser in chrome brave firefox chrome-ubo ; do
            docker run -d -v privacykpis.profiles.$profilenum:/tmp/profiles --privileged kaytwo/privacykpis:$browser --profile-index $profilenum
    done
done 