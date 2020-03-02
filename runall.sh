#!/bin/bash

echo starting 6 way measurement at `date`

for profilenum in 1 2 ; do
    echo "starting profile $profilenum"
    mkdir -p profiles.$profilenum
    echo "iterate through browsers"
    for browser in chrome brave firefox ; do
        echo "spawning $browser"
        while read url ; do 
            docker run -v `pwd`/profiles.$profilenum:/tmp/profiles --privileged --rm kaytwo/privacykpis:$browser $url ; 
        done < output/20200301.1k.urls.txt > output/20200302.$browser.$profilenum.jsonlines 2> output/20200302.$browser.$profilenum.errors &
    done
done 

wait

echo finished 6 way measurement at `date`