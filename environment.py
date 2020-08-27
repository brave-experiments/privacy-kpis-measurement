#!/usr/bin/env python3
import argparse
import sys

from privacykpis.consts import DEFAULT_PROXY_HOST, DEFAULT_PROXY_PORT
from privacykpis.consts import SUPPORTED_BROWSERS
import privacykpis.environment


PARSER = argparse.ArgumentParser(description="Setup the env for mitmproxy.")
PARSER.add_argument("--install", action="store_true",
                    help="Setting up the environment for measurement "
                    "(installing MITM certs, etc.)")
PARSER.add_argument("--uninstall", action="store_true",
                    help="Teardown the MITM environment after measurement.")
PARSER.add_argument("--case", required=True, choices=SUPPORTED_BROWSERS,
                    help="Which browser condition to test.")
PARSER.add_argument("--debug", action="store_true",
                    help="Print debugging information.")
PARSER.add_argument("--proxy-host", default=DEFAULT_PROXY_HOST,
                    help="The host to use when launching mitmproxy (only "
                    "used for MacOS).")
PARSER.add_argument("--proxy-port", default=DEFAULT_PROXY_PORT, type=int,
                    help="The port to use when launching mitmproxy (only "
                    "used for MacOS).")
PARSER.add_argument("--user", required=True,
                    help="The user that will be doing the crawling (only used "
                    "for chrome).")

ARGS = privacykpis.environment.Args(PARSER.parse_args())
if not ARGS.valid():
    sys.exit(-1)

privacykpis.environment.configure(ARGS)
