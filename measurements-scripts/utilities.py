import json, csv, os
import pandas as pd
import numpy as np 

OUTDIR = "plots/"
SPERTR = OUTDIR + "sites-per-tracker_B2/"
TLOC = OUTDIR + "token-locations_G10/"
TRPERCAT = OUTDIR + "trackers-per-category_D6/"
TRPERBR = OUTDIR + "trackers-per-browser_B1/"
TRPERDAT = OUTDIR + "trackers-per-browser_per_dataset_F8/"


def toPandasAndStore(data, filename):
	df = pd.DataFrame(data).transpose()
	df.sort_index().to_csv(filename, sep='\t', index = True, header=True)

flatten = lambda l: [item for sublist in l for item in sublist]

def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 

def getDateOfCrawl(filename):
	return filename.split("-2-")[-1].split("_")[0]


def getBrowser(filename):
	return filename.split("/")[-1].split("-2-")[0].rsplit("-", 1)[0]


def getStatistics(data):
	return {"1_min": np.min(data), "2_mean": np.mean(data), "3_max": np.max(data), "4_5th": np.percentile(data, 5), "5_25th": np.percentile(data, 25), "6_median": np.median(data), "7_75th": np.percentile(data, 75), "8_95th": np.percentile(data, 95)}


def readJson(file):
	with open(file) as json_file:
		data = json.load(json_file)
	return data


def plotCdf(data,filepath):
	total = 0
	occurences = {}
	for point in sorted(data):
		if point not in occurences: occurences[point] = 0
		occurences[point] += 1
	for point, count in occurences.items():
		total += count
	with open(filepath, 'w') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter='\t')
		csvwriter.writerow(["points", "occurences", "percentage", "cdf"])
		sumPerc = 0 
		for point, count in occurences.items():
			perc = float(count)*100/total
			sumPerc += perc
			csvwriter.writerow([point, count, perc, sumPerc])


def creat_folderTree():
	os.system('mkdir -p ' + OUTDIR)
	os.system('mkdir -p ' + TLOC)
	os.system('mkdir -p ' + TRPERCAT)
	os.system('mkdir -p ' + TRPERBR)
	os.system('mkdir -p ' + SPERTR)
	os.system('mkdir -p ' + TRPERDAT)
