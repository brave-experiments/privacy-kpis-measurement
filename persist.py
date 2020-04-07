#!/usr/bin/env python3
import argparse
import datetime
import sys

from networkx import write_gpickle

from privacykpis.argparse.types import writeable_path
import privacykpis.args
import privacykpis.persist


PARSER = argparse.ArgumentParser(description="Serialize requests as a graph.")
PARSER.add_argument("--input", nargs="*", required=True,
    type=argparse.FileType(encoding="utf-8"),
    help="A file with one or more JSON documents to record.",
    default=sys.stdin)
PARSER.add_argument("--multi", action="store_true", default=False,
    help="Read multiple JSON documents out of the input file.")
PARSER.add_argument("--output", required=True, type=writeable_path,
    help="Path to write the serialized graph to, in pickle format.")
PARSER.add_argument("--debug", action="store_true",
    help="Print debugging information.")

ARGS = privacykpis.args.PersistArgs(PARSER.parse_args())
if not ARGS.valid():
    sys.exit(-1)

GRAPH = privacykpis.persist.graph_from_args(ARGS)
OUTPUT_FILE = sys.stdout if ARGS.output is None else ARGS.output
write_gpickle(GRAPH, OUTPUT_FILE)
