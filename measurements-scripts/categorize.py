#!/usr/bin/env python3
import os, json, glob, sys
from adblockparser import AdblockRules

BLACKLIST_FILE = "./disconnect-blacklist.json"
indir = sys.argv[1]
REST = "Rest"

def readJsonFile(filename):
	with open(filename) as json_file:
		data = json.load(json_file)
	return data

def loadFilter():
	filterlist = {}
	entries = readJsonFile(BLACKLIST_FILE)['categories']
	for cat in entries.keys():
		for entry in entries[cat]:
			for name, value in entry.items():
				for toplevel, domains in value.items():
					for domain in domains:
						filterlist[domain] = cat
	return filterlist


if len(sys.argv) < 2: raise Exception("Error No input dir given")
# READ FILTERS
raw_rules=[]
with open("easylist.txt") as f:
    raw_rules = f.readlines()
rules = AdblockRules(raw_rules)
flist = loadFilter()
for file in glob.glob(indir+"*reidentification.json"):
	if "categories" in file:
		continue 
	print("Parsing",file)
	data = readJsonFile(file)
	for k,v in data.items():
		category = REST
		if k in flist:
			category = flist[k]
		if category == REST:
			if rules.should_block(k):
				category = "Easylist"
		v.update({"class":category})
	with open(file.split(".json")[0]+"_categories.json", 'w') as outfile:
		json.dump(data, outfile)
