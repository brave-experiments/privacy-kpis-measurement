#!/bin/bash

echo starting 8 way measurement at `date`

# get the alexa for today
TODAY=$(date '+%Y%m%d')
mkdir -p output
curl -s http://s3.amazonaws.com/alexa-static/top-1m.csv.zip |
funzip | head -n ${1:-1000} | awk -F, '{print "http://" $2}' > output/$TODAY.top1k.txt 

for profilenum in 1 2 ; do
    for browser in chrome brave firefox chrome-ubo ; do
        while read url ; do 
            docker run -v privacykpis.profiles.$profilenum:/tmp/profiles --privileged --rm kaytwo/privacykpis:$browser $url ; 
        done < output/$TODAY.top1k.txt > output/$TODAY.$browser.$profilenum.jsonlines 2> output/$TODAY.$browser.$profilenum.errors &
    done
done 

wait

echo finished 8 way measurement at `date`