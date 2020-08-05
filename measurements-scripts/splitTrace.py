#!/usr/bin/env python3
import fileinput
import json, os, sys, glob

if len(sys.argv) < 2:
    raise Exception("No input given")
indir = sys.argv[1]
outdir = "./browsers-traces1/"
handles = {}
os.system('mkdir -p ' + outdir)

for file in glob.glob(indir+"*.json"):
    if ".sample." in file:
        continue
    print("Spliting crawl",file)
    for line in open(file, "r").readlines():
        data = json.loads(line)
        channel = data["channel"]
        browser = data["browser"]
        date = data["date"]
        profile = data["profile"]
        name = outdir + '{}-{}-{}-{}.json'.format(browser, channel, profile, date)
        try:
            handle = handles[name]
        except KeyError:
            handle = open(name, 'w')
            handles[name] = handle
        handle.write(line + "\n")

for file in glob.glob(outdir+"*.json"):
    print("Serializing",file)
    os.system('python3 ../../privacy-kpis-measurement/serialize.py --input ' +
              file + ' --multi --output ' + file.split(".json")[0] + '.pickle --format pickle')