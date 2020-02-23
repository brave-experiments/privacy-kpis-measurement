#!/usr/bin/env python3
import argparse
import sys

import privacykpis.args
import privacykpis.common
from privacykpis.consts import SUPPORTED_BROWSERS
from privacykpis.consts import DEFAULT_PROXY_HOST, DEFAULT_PROXY_PORT


PARSER = argparse.ArgumentParser(description="Record HTTP request headers.")
PARSER.add_argument("--url", required=True,
    help="The URL to record the resulting network traffic of.")
PARSER.add_argument("--log", required=True,
    help="The path to record network traffic to, as a JSON text.")
PARSER.add_argument("--proxy-host", default=DEFAULT_PROXY_HOST,
    help="The host to use when launching mitmproxy (not supported with Firefox).")
PARSER.add_argument("--proxy-port", default=DEFAULT_PROXY_PORT, type=int,
    help="The port to use when launching mitmproxy (not supported with Firefox).")
PARSER.add_argument("--profile-path",
    help="Path to the browser profile to use (required except for Safari).")
PARSER.add_argument("--case", required=True, choices=SUPPORTED_BROWSERS,
    help="Which browser condition to test.")
PARSER.add_argument("--secs", default=30, type=int,
    help="Amount of time to allow the site to load for.")
PARSER.add_argument("--binary",
    help="Path to the browser binary to use (required except for Safari).")
PARSER.add_argument("--debug", action="store_true",
    help="Include debugging information.")

ARGS = privacykpis.args.MeasureArgs(PARSER.parse_args())
if not ARGS.valid():
    sys.exit(-1)

privacykpis.common.record(ARGS)
