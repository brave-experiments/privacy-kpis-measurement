#!/bin/bash

echo starting 6 way measurement at `date`

# get the alexa for today
TODAY=$(date '+%Y%m%d')
mkdir -p output
curl http://s3.amazonaws.com/alexa-static/top-1m.csv.zip > top-1m.csv.zip
unzip -c top-1m.csv.zip top-1m.csv | head -n 1000 | awk -F, '{print "http://" $2}' > output/$TODAY.top1k.txt 

for profilenum in 1 2 ; do
    echo "starting profile $profilenum"
    mkdir -p profiles.$profilenum
    echo "iterate through browsers"
    for browser in chrome brave firefox ; do
        echo "spawning $browser"
        while read url ; do 
            docker run -v `pwd`/profiles.$profilenum:/tmp/profiles --privileged --rm kaytwo/privacykpis:$browser $url ; 
        done < output/$TODAY.top1k.txt > output/$TODAY.$browser.$profilenum.jsonlines 2> output/$TODAY.$browser.$profilenum.errors &
    done
done 

wait

echo finished 6 way measurement at `date`