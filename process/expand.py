#!/usr/bin/env python3
import json
import pathlib
import sys

input_dir = pathlib.Path(sys.argv[1])
output_dir = sys.argv[2]

handles = {}
for input_file in input_dir.iterdir():
    if input_file.suffix != ".json":
        continue
    for line in input_file.open():
        data = json.loads(line)
        channel = data["channel"]
        browser = data["browser"]
        date = data["date"]
        profile = data["profile"]
        name = '{}-{}-{}-{}.json'.format(browser, channel, profile, date)
        try:
            handle = handles[name]
        except KeyError:
            handle = open(output_dir + "/" + name, 'w')
            handles[name] = handle
        handle.write(line + "\n")
