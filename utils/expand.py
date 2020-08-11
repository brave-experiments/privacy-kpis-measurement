#!/usr/bin/env python3
import fileinput
import json
handles = {}
for line in fileinput.input():
    data = json.loads(line)
    channel = data["channel"]
    browser = data["browser"]
    date = data["date"]
    profile = data["profile"]
    name = '{}-{}-{}-{}.json'.format(browser, channel, profile, date)
    try:
        handle = handles[name]
    except KeyError:
        handle = open(name, 'w')
        handles[name] = handle
    handle.write(line + "\n")
