#!/bin/bash
export HOME=/home/ckanich

cd /home/ckanich/repos/privacy-kpis-measurement
./runall.sh > todays_dockers
python3 source.py $1
python3 sink.py
gzip *.json && aws s3 cp *.json.gz s3://com.brave.research.privacykpis/ && rm *.json.gz
docker stop $(cat todays_dockers)
docker rm $(cat todays_dockers)
rm todays_dockers
