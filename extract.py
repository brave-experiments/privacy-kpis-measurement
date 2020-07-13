#!/usr/bin/env python3
import argparse
import pickle
import sys

from privacykpis.argparse.types import writeable_path
import privacykpis.serialize
from privacykpis.serialize import TrackingInstances


PARSER = argparse.ArgumentParser(description="Serialize tracking tokens.")
PARSER.add_argument("--input", required=True,
                    help="Path to a pickled BrowserMeasurement file.")
PARSER.add_argument("--control", required=False,
                    help="Path to another pickled BrowserMeasurement file, "
                         "used to determine which tokens are unique to a "
                         "session.")
PARSER.add_argument("--overlap", action="store_true", default=False,
                    help="Record the overlap between the two graphs, not "
                         "the difference. By default the difference is "
                         "recorded (ignored if --control is not passed).")
PARSER.add_argument("--output", required=True, type=writeable_path,
                    help="Path to write the serialized TrackingInstances data "
                         "to, in pickle format.")
PARSER.add_argument("--debug", action="store_true",
                    help="Print debugging information.")
PARSER.add_argument("--format", default="json",
                    choices=["json", "pickle"],
                    help="Version to serialize results to.")
ARGS = PARSER.parse_args()

INPUT = open(ARGS.input, 'rb')


def write_output(data: TrackingInstances) -> None:
    if ARGS.format == "json":
        data.to_json(open(ARGS.output, 'w'))
    elif ARGS.format == "pickle":
        data.to_pickle(open(ARGS.output, 'wb'))


MEASURE_GRAPH = pickle.load(INPUT)
MEASURE_TRACKING = MEASURE_GRAPH.get_tracking_instances()
if not ARGS.control:
    write_output(MEASURE_GRAPH)
    sys.exit(1)

CONTROL = open(ARGS.control, 'rb')
CONTROL_GRAPH = pickle.load(CONTROL)
CONTROL_TRACKING = CONTROL_GRAPH.get_tracking_instances()

RESULT = None
if ARGS.overlap:
    RESULT = TrackingInstances.overlap(MEASURE_TRACKING, CONTROL_TRACKING)
else:
    RESULT = TrackingInstances.difference(MEASURE_TRACKING, CONTROL_TRACKING)

write_output(RESULT)
sys.exit(1)
