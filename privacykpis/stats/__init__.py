import argparse
from functools import partial
import pickle
from typing import Any, cast, Dict, List, Optional, TextIO, Tuple, Union

import networkx  # type: ignore
from networkx import MultiDiGraph, read_gpickle

import privacykpis.args
from privacykpis.stats.filters import FilterFunc, should_include_token
import privacykpis.stats.filters
from privacykpis.stats.utilities import print_reidentification, print_keypair
from privacykpis.stats.utilities import prepare_output, print_json
from privacykpis.stats.utilities import kp_exists_in_control, get_origins
from privacykpis.stats.utilities import ReidentifyingOrgs, ReidentifyingOrgsAll
from privacykpis.stats.utilities import ReportWriters, KeyPairsOrigins
from privacykpis.consts import TOKEN_LOCATION, ORIGIN, TIMESTAMP, VALUE, KEY
from privacykpis.consts import TYPE, SITE
from privacykpis.tokenizing import TokenLocation
from privacykpis.types import CSVWriter, RequestRec


FORMATS = {"tsv", "json"}


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
        self.is_valid = True


def __reidentifying_pairs(fw: ReportWriters, ptokens: KeyPairsOrigins,
                          tp: str, control_kp: Optional[ReidentifyingOrgs],
                          filters: List[FilterFunc]
                          ) -> Tuple[List[RequestRec], ReidentifyingOrgs]:
    keyvals: List[RequestRec] = []
    reidentify: ReidentifyingOrgs = {}
    keypair_writer = fw["kp_tsv"] if "fw" in fw else None
    for k in ptokens:
        for obj in ptokens[k]:
            v = obj[VALUE]
            orgn = obj[ORIGIN]
            token_loc: TokenLocation = obj[TOKEN_LOCATION]
            if keypair_writer:
                keypair_writer = cast(CSVWriter, keypair_writer)
                print_keypair(keypair_writer, tp, k, v, orgn, token_loc,
                              obj[TIMESTAMP])
            keyvals.append({KEY: k, TOKEN_LOCATION: token_loc,
                            TIMESTAMP: obj[TIMESTAMP], VALUE: v,
                            ORIGIN: orgn})
            # filter based on control graph
            if kp_exists_in_control(control_kp, tp, k, v, orgn, token_loc):
                continue
            # filter based additional filters requested
            if not should_include_token(k, v, token_loc, filters):
                continue
            if k not in reidentify:
                reidentify[k] = {}
            if v not in reidentify[k]:
                reidentify[k][v] = {ORIGIN: [], TOKEN_LOCATION: str}
            reidentify[k][v][ORIGIN].append(orgn)
            reidentify[k][v][TOKEN_LOCATION] = token_loc
    return keyvals, reidentify


def __get_keypairs(org: str, req: RequestRec,
                   kpairs: KeyPairsOrigins) -> KeyPairsOrigins:
    for token_location in TokenLocation:
        tokens = req[token_location.name]
        if tokens is None:
            return kpairs
        for k, v in tokens:
            if k not in kpairs:
                kpairs[k] = []
            kpairs[k].append({ORIGIN: org, VALUE: v, TOKEN_LOCATION:
                             token_location.name, TIMESTAMP: req[TIMESTAMP]})
    return kpairs


def __process_graph(fw: ReportWriters, graph: MultiDiGraph,
                    control_kp: Optional[ReidentifyingOrgsAll],
                    filters: List[FilterFunc]) -> ReidentifyingOrgsAll:
    origins = get_origins(graph)
    kp_all = {}
    reident_all: ReidentifyingOrgsAll = {}
    for n, d in graph.nodes(data=True):
        # get 3party only
        if n is None or d[TYPE] == SITE:
            continue
        keypairs_orgs: KeyPairsOrigins = {}
        for origin in graph.predecessors(n):
            # check edge with origin
            if origin in origins and (origin, n) in graph.edges:
                reqs = graph.get_edge_data(origin, n)
                for i in reqs:
                    # get tokens for all origins associated with this 3party
                    request: RequestRec = reqs[i]
                    keypairs_orgs = __get_keypairs(origin, request,
                                                   keypairs_orgs)
        keyvals, reidentify = __reidentifying_pairs(fw, keypairs_orgs, n,
                                                    control_kp, filters)
        if len(keyvals) > 0:
            kp_all[n] = keyvals
        reident_all[n] = reidentify
    # better only on debug mode
    if "kp_json" in fw:
        kp_json_writer = cast(TextIO, fw["kp_json"])
        print_json(kp_json_writer, kp_all)
    return reident_all


def measure_samekey_difforigin(args: Args) -> None:
    fp: ReportWriters = prepare_output(args.input.name, args.format)
    input_graph: MultiDiGraph = read_gpickle(args.input.name)
    control_graph: Optional[MultiDiGraph] = None
    ctrl_reidentifying_kp: Optional[ReidentifyingOrgsAll] = None
    if args.control:
        control_graph = read_gpickle(args.control.name)
        print("Processing graph from", args.control.name)
        # TODO: theres gotta be a better way to structure this than None as the
        # writer argument
        # ctrl_reidentifying_kp = __process_graph(None, control_graph, None,
        #                                         args.filters)
    print("Processing graph from", args.input.name)
    reidentifying_kp = __process_graph(fp, input_graph, ctrl_reidentifying_kp,
                                       args.filters)
    print_reidentification(fp, reidentifying_kp)
