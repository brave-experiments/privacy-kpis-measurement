#!/usr/bin/env python3
import os, glob, threading, sys

indir = "./browsers-traces/"
outdir = "stat_results/"
os.system("mkdir -p " + outdir)


crawl = sys.argv[1]

for file in glob.glob(indir+"*"+crawl+".pickle"):
	threads = list()
	if "-1-" in file:
		continue
	else:
		thisdir = outdir + file.rsplit(".",1)[0].rsplit("/",1)[-1]
		print("Gets stats from",file)
		os.system("mkdir -p "+thisdir+'; python3 ../../privacy-kpis-measurement/stats.py --input ' +
			file + ' --filetypes --urls --dates --format json  --length 15 --control ' + 
			file.replace("-2-","-1-")+"; mv " + indir + "*"+crawl+".csv " + thisdir + " 2>/dev/null; mv " + 
			indir + "*"+crawl+".json " + thisdir+" 2>/dev/null")