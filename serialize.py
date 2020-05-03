#!/usr/bin/env python3
import argparse
import sys

from privacykpis.argparse.types import writeable_path
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
PARSER.add_argument("--format", default="pickle",
                    choices=privacykpis.serialize.FORMATS.keys(),
                    help="Format to serialize graph into.")

ARGS = privacykpis.serialize.Args(PARSER.parse_args())
if not ARGS.valid():
    sys.exit(-1)

GRAPH = privacykpis.serialize.graph_from_args(ARGS)
OUTPUT_FILE = sys.stdout if ARGS.output is None else ARGS.output
PREPROCESS_FUNC, WRITE_FUNC = privacykpis.serialize.FORMATS[ARGS.format]
PROCESSED_GRAPH = PREPROCESS_FUNC(GRAPH)
WRITE_FUNC(PROCESSED_GRAPH, OUTPUT_FILE)
