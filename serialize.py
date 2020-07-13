#!/usr/bin/env python3
import argparse
import sys

from privacykpis.argparse.types import writeable_path
from privacykpis.argparse.types import updateable_path
import privacykpis.serialize


PARSER = argparse.ArgumentParser(description="Serialize requests as a graph.")
PARSER.add_argument("--input", nargs="*", required=True,
                    type=argparse.FileType(encoding="utf-8"),
                    help="A file with one or more JSON documents to record.",
                    default=sys.stdin)
PARSER.add_argument("--multi", action="store_true", default=False,
                    help="Read multiple JSON documents out of the input file.")
PARSER.add_argument("--output", required=True, type=writeable_path,
                    help="Path to write the serialized graph to, in pickle "
                         "format.")
PARSER.add_argument("--debug", action="store_true",
                    help="Print debugging information.")
PARSER.add_argument("--redirect-cache", "-r", type=updateable_path,
                    help="If passed, use the passed file as a cache for "
                         "filtering out redirects.")

ARGS = privacykpis.serialize.Args(PARSER.parse_args())
if not ARGS.valid():
    sys.exit(-1)

GRAPH = privacykpis.serialize.graph_from_args(ARGS, ARGS.debug)
OUTPUT_FILE = sys.stdout if ARGS.output is None else ARGS.output
privacykpis.serialize.write(GRAPH, OUTPUT_FILE)
