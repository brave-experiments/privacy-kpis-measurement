import argparse
from functools import partial
import pickle
from typing import Any, cast, Dict, List, Optional, TextIO, Tuple, Union

import networkx  # type: ignore
from networkx import MultiDiGraph, read_gpickle

import privacykpis.args
from privacykpis.stats.filters import FilterFunc, should_include_token
from privacykpis.stats.filters import kp_exists_in_control
import privacykpis.stats.filters
from privacykpis.stats.utilities import print_reidentification, print_keypair
from privacykpis.stats.utilities import prepare_output, print_json, get_origins
from privacykpis.stats.utilities import ReidentifyingOrgs, ReidentifyingOrgsAll
from privacykpis.stats.utilities import ReportWriters, KeyPairsOrigins
from privacykpis.consts import TOKEN_LOCATION, ORIGIN, TIMESTAMP, VALUE, KEY
from privacykpis.consts import TYPE, SITE
from privacykpis.tokenizing import TokenLocation
from privacykpis.types import CSVWriter, RequestRec


FORMATS = {"csv", "json"}


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


def __reidentifying_pairs(fw: ReportWriters, tp: str, ptokens: KeyPairsOrigins,
                          control_kp: Optional[ReidentifyingOrgs],
                          filters: List[FilterFunc]
                          ) -> ReidentifyingOrgs:
    reidentify: ReidentifyingOrgs = {}
    keypair_writer = cast(CSVWriter, fw["kp_csv"]) if "kp_csv" in fw else None
    for k in ptokens:
        for obj in ptokens[k]:
            v = obj[VALUE]
            orgn = obj[ORIGIN]
            token_loc: TokenLocation = obj[TOKEN_LOCATION]
            # enabled only on debug mode
            if keypair_writer:
                print_keypair(keypair_writer, tp, k, v, orgn, token_loc,
                              obj[TIMESTAMP])
            # filter based on control graph
            if kp_exists_in_control(control_kp, tp, k, v, orgn, token_loc):
                continue
            # filter based on additional filters requested
            if not should_include_token(k, v, token_loc, filters):
                continue
            if k not in reidentify:
                reidentify[k] = {}
            if v not in reidentify[k]:
                reidentify[k][v] = {ORIGIN: [], TOKEN_LOCATION: str}
            reidentify[k][v][ORIGIN].append(orgn)
            reidentify[k][v][TOKEN_LOCATION] = token_loc
    return reidentify


def __get_keypairs(org: str, req: RequestRec,
                   kpairs: KeyPairsOrigins) -> KeyPairsOrigins:
    for token_location in TokenLocation:
        tokens = req[token_location.name]
        if tokens is None:
            continue
        for k, v in tokens:
            if k not in kpairs:
                kpairs[k] = []
            kpairs[k].append({ORIGIN: org, VALUE: v, TOKEN_LOCATION:
                             token_location, TIMESTAMP: req[TIMESTAMP]})
    return kpairs


def __process_graph(graph: MultiDiGraph, filters: List[FilterFunc],
                    control_kp: Optional[ReidentifyingOrgsAll],
                    fw: ReportWriters) -> ReidentifyingOrgsAll:
    origins = get_origins(graph)
    reident_all: ReidentifyingOrgsAll = {}
    for n, d in graph.nodes(data=True):
        # get 3party only
        if n is None or d[TYPE] == SITE:
            continue
        kp_orgs: KeyPairsOrigins = {}
        for origin in graph.predecessors(n):
            # check edge with origin
            if origin in origins and (origin, n) in graph.edges:
                reqs = graph.get_edge_data(origin, n)
                for i in reqs:
                    # get tokens for all origins associated with this 3party
                    request: RequestRec = reqs[i]
                    kp_orgs = __get_keypairs(origin, request, kp_orgs)
        reident_all[n] = __reidentifying_pairs(fw, n, kp_orgs, control_kp,
                                               filters)
    return reident_all


def measure_samekey_difforigin(args: Args) -> None:
    (fp, fc) = prepare_output(args.input.name, args.format, args.debug)
    input_graph: MultiDiGraph = read_gpickle(args.input.name)
    control_graph: Optional[MultiDiGraph] = None
    ctrl_reidentifying_kp: Optional[ReidentifyingOrgsAll] = None
    if args.control:
        control_graph = read_gpickle(args.control.name)
        print("Processing graph from", args.control.name)
        ctrl_reidentifying_kp = __process_graph(control_graph, args.filters,
                                                ctrl_reidentifying_kp, fc)
    print("Processing graph from", args.input.name)
    reidentifying_kp = __process_graph(input_graph, args.filters,
                                       ctrl_reidentifying_kp, fp)
    print_reidentification(fp, reidentifying_kp)
