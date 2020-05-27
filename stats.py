#!/usr/bin/env python3
import argparse
import sys

import privacykpis.stats


PARSER = argparse.ArgumentParser(description="Extract statistics from "
                                 "serialized graphs.")
PARSER.add_argument("--input", "-i",
                    required=True, type=argparse.FileType(encoding="utf-8"),
                    help="Serialized networkx graph to extract statistics "
                    "from.")
PARSER.add_argument("--control", "-c",
                    type=argparse.FileType(encoding="utf-8"),
                    help="If provided, used as the control crawl (to remove "
                    "non-identifying strings) when extracting statistics.")
PARSER.add_argument("--format", "-f", default="json",
                    choices=privacykpis.stats.FORMATS,
                    help="Format to store output.")
PARSER.add_argument("--debug", action="store_true",
                    help="Print debugging information.")
PARSER.add_argument("--length", "-l", type=int,
                    help="Filter param values based on their length.")
PARSER.add_argument("--filetypes", "-nf", action="store_true",
                    help="Detect and filter out possible filenames with "
                    "known filetypes from param values.")
PARSER.add_argument("--dates", "-nd", action="store_true",
                    help="Detect and filter out possible date strings from "
                    "param values.")

ARGS = privacykpis.stats.Args(PARSER.parse_args())
if not ARGS.valid():
    sys.exit(-1)
if ARGS.debug:
    print("Debug mode on")
privacykpis.stats.measure_samekey_difforigin(ARGS)
