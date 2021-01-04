#!/usr/bin/env python3
import argparse
import json
import sys
from urllib.parse import urlparse


PARSER = argparse.ArgumentParser("Search for records in request data.")
PARSER.add_argument("-i", "--input",
                    help="The JSON file to query. If not provided, uses " +
                         "stdin.")
PARSER.add_argument("-f", "--first-party",
                    help="If provided, the first party requests to filter " +
                         "by (i.e., only show requests where the input " +
                         "appears in the URL of the first party.")
PARSER.add_argument("-t", "--request",
                    help="If provided, filter requests down to only those "
                         "where the given string appears in the URL of a "
                         "sub-resource request.")
PARSER.add_argument("-b", "--body", action="store_true",
                    help="Include the body of the request in the report.")
PARSER.add_argument("-d", "--headers", action="store_true",
                    help="Include request headers in the report.")
PARSER.add_argument("-n", "--header-name",
                    help="If provided, only include matching headers.")
ARGS = PARSER.parse_args()

INPUT_HANDLE = open(ARGS.input, 'r') if ARGS.input else sys.stdin
REPORT = []

for line in INPUT_HANDLE:
    data_record = json.loads(line)
    report_entry = {}
    site_url = data_record["url"]
    site_host = urlparse(data_record["url"]).hostname
    if ARGS.first_party and ARGS.first_party not in site_host:
        continue
    report_entry["site"] = site_url

    for request in data_record["requests"]:
        request_url = request["url"]
        if ARGS.request:
            request_host = urlparse(request_url).hostname
            if ARGS.request not in request_host:
                continue

        report_entry["request"] = request_url
        if ARGS.body:
            report_entry["body"] = request["body"]

        if not ARGS.headers and not ARGS.header_name:
            continue

        report_entry["headers"] = []
        for name, value in request["headers"].items():
            if ARGS.header_name:
                if ARGS.header_name in name:
                    report_entry["headers"].append([name, value])
                continue
            if ARGS.headers:
                report_entry["headers"].append([name, value])
    REPORT.append(report_entry)

json.dump(REPORT, sys.stdout)
