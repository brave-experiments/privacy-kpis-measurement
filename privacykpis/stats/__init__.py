import argparse
from functools import partial
import pickle
from typing import Any, cast, Dict, List, Optional, TextIO, Tuple, Union

import networkx  # type: ignore
from networkx import MultiDiGraph, read_gpickle

import privacykpis.args
from privacykpis.stats.filters import FilterFunc, should_include_token
from privacykpis.stats.filters import kp_exists_in_control
from privacykpis.stats.utilities import print_reidentifiying_tokens
from privacykpis.stats.utilities import get_origins
from privacykpis.stats.utilities import prepare_output, print_to_csv
from privacykpis.stats.utilities import ReidentifyingPairs, ReportWriters
from privacykpis.consts import TOKEN_LOCATION, ORIGIN, TIMESTAMP
from privacykpis.consts import NODE_TYPE, SITE, TOKEN_VALUE, TOKEN_KEY
from privacykpis.tokenizing import TokenLocation
from privacykpis.types import CSVWriter, RequestRec


FORMATS = {"csv", "json"}
TokenKeypair = Dict[str, List[RequestRec]]


class Args(privacykpis.args.Args):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        filters: List[FilterFunc] = []

        if args.length:
            if args.length <= 0:
                privacykpis.common.err("if filtering by token length, length"
                                       "arg must be positive")
                return
            min_len_filter = partial(privacykpis.stats.filters.length,
                                     min_length=args.length)
            filters.append(min_len_filter)
        if args.filetypes:
            filters.append(privacykpis.stats.filters.filetypes)
        if args.dates:
            filters.append(privacykpis.stats.filters.dates)
        self.input = args.input
        self.control = args.control
        self.format = args.format
        self.filters = filters
        self.debug = args.debug
        self.is_valid = True


# retrieve token keypairs that allow reidentification across origins
def __reidentifying_pairs(fw: ReportWriters, tparty: str,
                          tokens_kp: TokenKeypair,
                          control_kp: Optional[ReidentifyingPairs],
                          filters: List[FilterFunc]
                          ) -> ReidentifyingPairs:
    rid_pairs: ReidentifyingPairs = {}
    kp_writer_debug = cast(CSVWriter, fw["kp_csv"]) if "kp_csv" in fw else None
    for token_k in tokens_kp:
        for token_info in tokens_kp[token_k]:
            token_v = token_info[TOKEN_VALUE]
            origin = token_info[ORIGIN]
            token_timestmp = token_info[TIMESTAMP]
            token_loc: TokenLocation = token_info[TOKEN_LOCATION]
            # enabled only on debug mode
            if kp_writer_debug:
                row = [tparty, token_k, token_v, origin,
                       token_loc, token_timestmp]
                print_to_csv(kp_writer_debug, row)
            # filter based on control graph
            if kp_exists_in_control(control_kp, tparty, token_k, token_v,
                                    origin, token_loc):
                continue
            # filter based on additional filters requested
            if not should_include_token(token_k, token_v, token_loc, filters):
                continue
            if token_k not in rid_pairs:
                rid_pairs[token_k] = {}
            if token_v not in rid_pairs[token_k]:
                rid_pairs[token_k][token_v] = {ORIGIN: [], TOKEN_LOCATION: str}
            rid_pairs[token_k][token_v][ORIGIN].append(origin)
            rid_pairs[token_k][token_v][TOKEN_LOCATION] = token_loc
    return rid_pairs


# function to extract token key-pairs from edges
def __get_keypairs(org: str, req: RequestRec,
                   kpairs: TokenKeypair) -> TokenKeypair:
    for token_location in TokenLocation:
        tokens = req[token_location.name]
        if tokens is None:
            continue
        for token_k, token_v in tokens:
            if token_k not in kpairs:
                kpairs[token_k] = []
            kpairs[token_k].append({ORIGIN: org, TOKEN_VALUE: token_v,
                                   TOKEN_LOCATION: token_location,
                                   TIMESTAMP: req[TIMESTAMP]})
    return kpairs


# function to traverse and extract information from graph
def __process_graph(graph: MultiDiGraph, filters: List[FilterFunc],
                    control_kp: Optional[Dict[str, ReidentifyingPairs]],
                    fw: ReportWriters) -> Dict[str, ReidentifyingPairs]:
    origins = get_origins(graph)
    reident_all: Dict[str, ReidentifyingPairs] = {}
    for n, d in graph.nodes(data=True):
        # get 3party only
        if n is None or d[NODE_TYPE] == SITE:
            continue
        token_kp: TokenKeypair = {}
        for origin in graph.predecessors(n):
            # check edge with origin
            if origin in origins and (origin, n) in graph.edges:
                reqs = graph.get_edge_data(origin, n)
                for i in reqs:
                    # get token pairs of all reqs associated with this 3party
                    request: RequestRec = reqs[i]
                    token_kp = __get_keypairs(origin, request, token_kp)
        # retrieve tokens that allow reidentification across origins
        reident_all[n] = __reidentifying_pairs(fw, n, token_kp, control_kp,
                                               filters)
    return reident_all


def measure_samekey_difforigin(args: Args) -> None:
    (fp, fc) = prepare_output(args.input.name, args.format, args.debug)
    input_graph: MultiDiGraph = read_gpickle(args.input.name)
    control_graph: Optional[MultiDiGraph] = None
    ctrl_reidentifying_kp: Optional[Dict[str, ReidentifyingPairs]] = None
    if args.control:
        control_graph = read_gpickle(args.control.name)
        if control_graph is None:
            raise ValueError('None value in control graph')
        print("Processing graph from", args.control.name)
        ctrl_reidentifying_kp = __process_graph(control_graph, args.filters,
                                                ctrl_reidentifying_kp, fc)
    print("Processing graph from", args.input.name)
    reidentifying_kp = __process_graph(input_graph, args.filters,
                                       ctrl_reidentifying_kp, fp)
    print_reidentifiying_tokens(fp, reidentifying_kp)
