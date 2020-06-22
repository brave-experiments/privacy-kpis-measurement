#!/bin/bash

echo starting 8 way measurement at `date`

for profilenum in 1 2 ; do
    for browser in chrome brave firefox chrome-ubo ; do
            docker run -d -v privacykpis.profiles.$profilenum:/tmp/profiles --privileged --rm kaytwo/privacykpis:$browser --profile-index $profilenum
    done
done 

echo finished 8 way measurement at `date`
