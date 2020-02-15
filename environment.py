#!/usr/bin/env python3
import argparse
import sys

import privacykpis.args
import privacykpis.common
from privacykpis.consts import SUPPORTED_BROWSERS


PARSER = argparse.ArgumentParser(description="Setup the env for mitmproxy.")
PARSER.add_argument("--install", action="store_true",
    help="Setting up the environment for measurement (installing MITM certs, etc.)")
PARSER.add_argument("--uninstall", action="store_true",
    help="Teardown the MITM environment after measurement.")
PARSER.add_argument("--case", required=True, choices=SUPPORTED_BROWSERS,
    help="Which browser condition to test.")

ARGS = privacykpis.args.ConfigArgs(PARSER.parse_args())
if not ARGS.valid():
    sys.exit(-1)

privacykpis.common.configure_env(ARGS)
