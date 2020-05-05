import argparse
import pickle
from typing import Optional

import networkx
from networkx import read_gpickle

import privacykpis.args


class Args(privacykpis.args.Args):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.input = args.input
        self.control = args.control
        self.is_valid = True


def requested_sites_subgraphs(graph: networkx.MultiDiGraph):
    pass


def measure(args: Args):
    input_graph: networkx.MultiDiGraph = read_gpickle(args.input)
    control_graph: Optional[networkx.MultiDiGraph]
    if args.control:
        control_graph = read_gpickle(args.control)
    else:
        args.control = None
