#!/usr/bin/env python3
import argparse
import sys

import privacykpis.args
import privacykpis.common

PARSER = argparse.ArgumentParser(description="Record HTTP request headers.")
PARSER.add_argument("--url", required=True,
  help="The URL to record the resulting network traffic of.")
PARSER.add_argument("--log", required=True,
  help="The path to record network traffic to, as a JSON text.")
PARSER.add_argument("--proxy-host", default="127.0.0.1",
  help="The host to use when launching mitmproxy.")
PARSER.add_argument("--proxy-port", default=8888, type=int,
  help="The port to use when launching mitmproxy.")
PARSER.add_argument("--profile-path",
  help="Path to the browser profile to use (required except for Safari).")
PARSER.add_argument("--case", required=True, choices=["safari", "chrome"],
  help="Which browser condition to test.")
PARSER.add_argument("--secs", default=30, type=int,
  help="Amount of time to allow the site to load for.")
PARSER.add_argument("--binary",
  help="Path to the browser binary to use (required except for Safari).")


ARGS = privacykpis.args.Args(PARSER.parse_args())
if not ARGS.valid():
  sys.exit(-1)

privacykpis.common.record(ARGS)