import csv, glob
import pandas as pd
import numpy as np 
from utilities import *

def get_tokenLocations(data, token_locations_all, browser):
	if browser not in token_locations_all: token_locations_all[browser] = {}
	locations = {}
	for tp, tokens in data.items():
		for token in tokens:
			loc_type = token["token_location"]
			if loc_type not in locations: locations[loc_type] = 0
			locations[loc_type] += 1
	for loc_type, count in locations.items():
		if loc_type not in token_locations_all[browser]: token_locations_all[browser][loc_type] = [] 
		token_locations_all[browser][loc_type].append(count)
	return token_locations_all


def plot_perCategories(path):
	classes = {}
	for file in glob.glob(path+"*.json"):
		data = readJson(file)
		date = getDateOfCrawl(file)
		browser = getBrowser(file)
		if browser not in classes: classes[browser] = {}
		if date not in classes[browser]: classes[browser][date] = {}
		for tp, vals in data.items():
			count1p = vals['num_of_sites_reidentifies']
			category = vals['class']
			if count1p == 0: continue
			if category not in classes[browser][date]: classes[browser][date][category] = []
			classes[browser][date][category].append(count1p) 
	if classes==None: return
	allBrowsers = {}
	for browser, crawls in classes.items():
		perCatStats = {}
		for crawl, cats in crawls.items():
			for category, vals in cats.items():
				if category not in perCatStats: perCatStats[category] = {}
				for k,v in getStatistics(vals).items():
					if k not in perCatStats[category]: perCatStats[category][k] = []
					perCatStats[category][k].append(v)
		avgStatsPerCategory = {}
		for category, stats in perCatStats.items():
			if category not in avgStatsPerCategory: avgStatsPerCategory[category] = {}
			if category not in allBrowsers: allBrowsers[category] = {}
			for stat_k, stat_v in stats.items():			
				avgStatsPerCategory[category][stat_k] = np.mean(stat_v)
				if stat_k not in allBrowsers[category]: allBrowsers[category][stat_k] = []
				allBrowsers[category][stat_k].append(np.mean(stat_v))
		toPandasAndStore(avgStatsPerCategory, TRPERCAT + browser + "_3p_per_category.tsv")
	# across all browsers
	avgAllBrowsers = {}
	for category, stats in allBrowsers.items():
		for stat_k, stat_v in stats.items():
			if category not in avgAllBrowsers: avgAllBrowsers[category] = {}
			avgAllBrowsers[category][stat_k] = np.mean(stat_v)
	toPandasAndStore(avgAllBrowsers, TRPERCAT + "all_browsers_3p_per_category.tsv")


def get_tpPerBrowser(data, browser, tpPerBrowser):
	if browser not in tpPerBrowser: tpPerBrowser[browser] = []
	tpPerBrowser[browser].append(list(data.keys()))
	return tpPerBrowser


def get_tpPerBrowser_perc(data, browser, date, tpPerBrowser_perCrawl):
	if browser not in tpPerBrowser_perCrawl: tpPerBrowser_perCrawl[browser] = {}
	if date not in tpPerBrowser_perCrawl[browser]: tpPerBrowser_perCrawl[browser][date] = []
	tpPerBrowser_perCrawl[browser][date].append(list(data.keys()))
	return tpPerBrowser_perCrawl


def get_numOffirstpPerThirdp(data, browser, fpPerTp):
	if browser not in fpPerTp: fpPerTp[browser] = []
	for tp, tokens in data.items():
		for token in tokens:
			for k in token.keys():
				if "sites_reidentifies" in k:
					fpPerTp[browser].append(token[k])
	return fpPerTp


def plot_numOffirstpPerThirdp(fpPerTp, dataset):
	totals = {}
	for browser, num_of_sites_all in fpPerTp.items():
		plotCdf(num_of_sites_all, SPERTR +browser+"-"+dataset+"-fp_per_tp_cdf.tsv")		


def get_abs_tpsPerBrowser(data):
	absolutes = {}
	for browser, tps in data.items():
		if browser not in absolutes: absolutes[browser] = []
		for crawl in tps:
			absolutes[browser].append(len(crawl))
	return absolutes


def get_perc_tpsPerBrowser(data,totalTps):
	perc = {}
	total_per_day = {}
	dates = list(totalTps.keys())
	for date in dates:
		if date not in total_per_day: total_per_day[date] = []
		total_per_day[date] = list(np.unique(flatten(totalTps[date])))

	for browser, crawls in data.items():
		if browser not in perc: perc[browser] = []
		for date, crawl in crawls.items():
			flat_crawl = flatten(crawl)
			perc[browser].append(float(len(intersection(flat_crawl,total_per_day[date])))*100/len(total_per_day[date]))
	return perc


def plot_tpPerBrowser(tpPerBrowser, alexa_tpPerBrowser, tw_tpPerBrowser):
	if len(tpPerBrowser.keys()) == 0 or len(tw_tpPerBrowser.keys()) == 0 or len(alexa_tpPerBrowser.keys()) == 0: return
	absolutes = get_abs_tpsPerBrowser(tpPerBrowser)
	alexa_absolutes = get_abs_tpsPerBrowser(alexa_tpPerBrowser)
	tw_absolutes = get_abs_tpsPerBrowser(tw_tpPerBrowser)
	tpPerBrowser_toCSV("absolutes",absolutes, alexa_absolutes, tw_absolutes)
	

def plot_tpPerBrowser_perc(tpPerBrowser, alexa_tpPerBrowser, tw_tpPerBrowser, alltps, alexa_alltps, tw_alltps):
	perc = get_perc_tpsPerBrowser(tpPerBrowser, alltps)
	alexa_perc = get_perc_tpsPerBrowser(alexa_tpPerBrowser, alexa_alltps)
	tw_perc = get_perc_tpsPerBrowser(tw_tpPerBrowser, tw_alltps)
	tpPerBrowser_toCSV("percentages", perc, alexa_perc, tw_perc)


def tpPerBrowser_toCSV(postfix, data, alexa_data, tw_data):
	with open(TRPERBR + "tpPerBrowser_"+postfix+".tsv", 'w') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter='\t')
		csvwriter.writerow(["browser", "all_third_parties", "alexa_third_parties", "tw_third_parties"])
		for browser in data.keys():
			csvwriter.writerow([browser, np.mean(data[browser]),
								np.mean(alexa_data[browser]),
								np.mean(tw_data[browser])])


def plot_tokenLocations(locations_all, prefix):
	if len(locations_all) == 0: return
	with open(TLOC +prefix+"_token_locations.tsv", 'w') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter='\t')
		location_types = sorted(list(locations_all[list(locations_all.keys())[0]].keys()))
		headers = ["browser"]
		for item in location_types:
			headers.append((item+"-ABS").replace("_","-").lower())
			headers.append(item.replace("_","-").lower())
		csvwriter.writerow(headers)
		for browser in sorted(locations_all.keys()):
			locations = locations_all[browser]
			total = 0
			for loc_k in location_types:
				total += np.mean(locations[loc_k])
			results = [browser]
			for loc_k in location_types:
				results.append(np.mean(locations[loc_k]))
				results.append(float(np.mean(locations[loc_k])*100)/np.mean(total))
			csvwriter.writerow(results)