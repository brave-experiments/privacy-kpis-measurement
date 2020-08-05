#!/usr/bin/env python3

import sys
from utilities import *
from ops import *

VERBOSE = "*reidentification_verbose.json"

def dispatcher(indir):
	token_locations = {}
	tpPerBrowser = {}; tpPerBrowser_perCrawl = {}
	alexa_tpPerBrowser = {}; alexa_tpPerBrowser_perCrawl = {}
	tw_tpPerBrowser = {}; tw_tpPerBrowser_perCrawl = {}
	tw_token_locations = {}
	alexa_token_locations = {}
	fpPerTp = {}
	tw_fpPerTp = {}
	alexa_fpPerTp = {}
	alexa_allTps = {}
	tw_allTps = {}
	allTps = {}
	# parse verbose data
	for file in glob.glob(indir + VERBOSE):
		data = readJson(file)
		date = getDateOfCrawl(file)
		browser = getBrowser(file)
		if "alexa" in file:
			alexa_tpPerBrowser = get_tpPerBrowser(data, browser, alexa_tpPerBrowser)  #B1
			alexa_token_locations = get_tokenLocations(data, alexa_token_locations, browser) #G10
			alexa_fpPerTp = get_numOffirstpPerThirdp(data, browser, alexa_fpPerTp) #B2
			if date not in alexa_allTps: alexa_allTps[date] = []
			alexa_allTps[date].append(list(data.keys()))
			alexa_tpPerBrowser_perCrawl = get_tpPerBrowser_perc(data, browser, date, alexa_tpPerBrowser_perCrawl)		
		if "twitter" in file:
			tw_tpPerBrowser = get_tpPerBrowser(data, browser, tw_tpPerBrowser)  #B1
			tw_token_locations = get_tokenLocations(data, tw_token_locations, browser) #G10
			tw_fpPerTp = get_numOffirstpPerThirdp(data, browser, tw_fpPerTp) #B2
			if date not in tw_allTps: tw_allTps[date] = []
			tw_allTps[date].append(list(data.keys()))
			tw_tpPerBrowser_perCrawl = get_tpPerBrowser_perc(data, browser, date, tw_tpPerBrowser_perCrawl)

		if date not in allTps: allTps[date] = []
		allTps[date].append(list(data.keys()))
		token_locations = get_tokenLocations(data, token_locations, browser) #G10
		tpPerBrowser = get_tpPerBrowser(data, browser, tpPerBrowser) #B1
		fpPerTp = get_numOffirstpPerThirdp(data, browser, fpPerTp) #B2
		tpPerBrowser_perCrawl = get_tpPerBrowser_perc(data, browser, date, tpPerBrowser_perCrawl)
	
		#start plotting results	
	plot_tpPerBrowser(tpPerBrowser, alexa_tpPerBrowser, tw_tpPerBrowser)
	plot_tpPerBrowser_perc(tpPerBrowser_perCrawl, alexa_tpPerBrowser_perCrawl, tw_tpPerBrowser_perCrawl,
							allTps, alexa_allTps, tw_allTps) #B1
	plot_perCategories(indir + "content_categories/") #D6
	plot_tokenLocations(token_locations,"all") #G10
	plot_tokenLocations(tw_token_locations,"twitter") #G10
	plot_tokenLocations(alexa_token_locations,"alexa") #G10
	plot_numOffirstpPerThirdp(fpPerTp, "all") #B2
	plot_numOffirstpPerThirdp(tw_fpPerTp, "twitter") #B2
	plot_numOffirstpPerThirdp(alexa_fpPerTp, "alexa") #B2
	

if len(sys.argv) < 2: raise Exception("Error No input dir given")
indir = sys.argv[1]
creat_folderTree()
dispatcher(indir)