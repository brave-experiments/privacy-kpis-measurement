#!/usr/bin/env python3
import argparse
import json
import sys

import redis

from privacykpis.consts import SUPPORTED_BROWSERS
from privacykpis.consts import DEFAULT_PROXY_HOST, DEFAULT_PROXY_PORT
import privacykpis.record


PARSER = argparse.ArgumentParser(description="Record HTTP request headers.")
# either scrape one URL:
PARSER.add_argument("--url",
                    help="The URL to record the resulting network traffic of.")
# or listen on a queue and scrape continuously:
PARSER.add_argument("--queue-host",
                    help="redis host for queued URL scrape requests.")
PARSER.add_argument("--queue-port", default=6379, type=int,
                    help="Non-standard redis port for URL queue.")
PARSER.add_argument("--output-queue", default="queue:output",
                    help="Where to send the json blob results (in redis).")
PARSER.add_argument("--profile-index",
                    help="Which profile queue to consume urls from.")

PARSER.add_argument("--log", required=True,
                    help="The path to record network traffic to, as a "
                    "JSON text.")
PARSER.add_argument("--proxy-host", default=DEFAULT_PROXY_HOST,
                    help="The host to use when launching mitmproxy (only "
                    "supported w/ Chrome).")
PARSER.add_argument("--proxy-port", default=DEFAULT_PROXY_PORT, type=int,
                    help="The port to use when launching mitmproxy (only "
                    "supported w/ Chrome).")
PARSER.add_argument("--profile-path",
                    help="Path to the browser profile to use (required except "
                    "for Safari).")
PARSER.add_argument("--case", required=True, choices=SUPPORTED_BROWSERS,
                    help="Which browser condition to test.")
PARSER.add_argument("--secs", default=30, type=int,
                    help="Amount of time to allow the site to load for.")
PARSER.add_argument("--binary",
                    help="Path to the browser binary to use (required except "
                    "for Safari).")
PARSER.add_argument("--debug", action="store_true",
                    help="Print debugging information.")

ARGS = privacykpis.record.Args(PARSER.parse_args())
if not ARGS.valid():
    sys.exit(-1)

if ARGS.url:
    privacykpis.record.run(ARGS)
else:
    """
    Wait on a specific redis queue, record urls as you get them
    """
    while True:
        conn = redis.Redis(ARGS.queue_host)
        packed = conn.blpop(['queue:%s:%s' % (ARGS.case, ARGS.profile_index)], 30)
        if not packed:
            continue
        to_scrape = json.loads(packed[1].decode('utf-8'))
        ARGS.url = to_scrape['url']
        print("scraping %s" % ARGS.url)
        privacykpis.record.run(ARGS)
        with open(ARGS.log) as f:
            content = json.loads(f.read())
            content['channel'] = to_scrape['channel']
            content['date'] = to_scrape['date']
            content['browser'] = ARGS.case
            content['profile'] = ARGS.profile_index
            conn.rpush(ARGS.output_queue, json.dumps(content))
        # todo: push the result onto the queue
