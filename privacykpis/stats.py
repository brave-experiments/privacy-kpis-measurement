import argparse
import pickle
import networkx  # type: ignore
from networkx import MultiDiGraph, read_gpickle
from typing import TextIO, Dict, List, Optional, Tuple, Any
import privacykpis.args
from privacykpis.stats_utilities import *
from privacykpis.stats_filters import *


FORMATS = {"tsv", "json"}
FILTER_PREFIX = "filter_"


class Args(privacykpis.args.Args):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.input = args.input
        self.control = args.control
        self.format = args.format
        self.is_valid = True
        self.filters = {}
        for argkey in args.__dict__.keys():
            if FILTER_PREFIX in argkey:
                self.filters[argkey] = args.__dict__[argkey]


def __reidentifying_pairs(fw: Optional[Fpointers], ptokens: KeyPairsOrigins,
                          tp: str, control_kp: Optional[ReidentifyingOrgs],
                          filter: Optional[FiltersApplied]
                          ) -> Tuple[List[Dict[str, Any]], ReidentifyingOrgs]:
    keyvals = []
    reidentify: ReidentifyingOrgs = {}
    for k in ptokens:
        for obj in ptokens[k]:
            v = obj["val"]
            origin = obj["origin"]
            ttype = obj["token_type"]
            print_KeyPair(fw, tp, k, v, origin, ttype,
                          obj["timestamp"])
            keyvals.append({"key": k, "token_type": ttype,
                            "timestamp": obj["timestamp"], "val": v,
                            "origin": origin})
            # filter based on control graph
            if not kp_exists_in_control(control_kp, tp, k, v, origin, ttype):
                # filter based additional filters requested
                if not apply_filters(k, v, ttype, filter):
                    if k not in reidentify:
                        reidentify[k] = {}
                    if v not in reidentify[k]:
                        reidentify[k][v] = {"origins": [], "token_type": str}
                    reidentify[k][v]["origins"].append(origin)
                    reidentify[k][v]["token_type"] = ttype
    return keyvals, reidentify


def __get_keypairs(o: str, req: Dict[str, Any],
                   kpairs: KeyPairsOrigins) -> KeyPairsOrigins:
    tkeys = ["cookies tokens", "path tokens", "query tokens", "body tokens"]
    for tk in tkeys:
        kpairs = __demul_token(o, req, tk, kpairs)
    return kpairs


def __demul_token(o: str, req: Dict[str, Any], token_type: str,
                  kpairs: KeyPairsOrigins) -> KeyPairsOrigins:
    tokens = req[token_type]
    if tokens is None:
        return kpairs
    for (k, v) in tokens:
        if k not in kpairs:
            kpairs[k] = []
        kpairs[k].append({"origin": o, "val": v, "token_type": token_type,
                         "timestamp": req["timestamp"]})
    return kpairs


def __process_graph(fw: Optional[Fpointers], graph: MultiDiGraph, control_kp:
                    Optional[ReidentifyingOrgs_all], filter:
                    Optional[FiltersApplied]) -> ReidentifyingOrgs_all:
    origins = get_origins(graph)
    kp_all = {}
    reident_all: ReidentifyingOrgs_all = {}
    for n, d in list(graph.nodes(data=True)):
        # get 3party only
        if n is None or d["type"] == "site":
            continue
        keypairs_orgs: KeyPairsOrigins = {}
        for o in graph.predecessors(n):
            # check edge with origin
            if o in origins and (o, n) in graph.edges:
                reqs = graph.get_edge_data(o, n)
                for i in reqs:
                    # get tokens for all origins associated with this 3party
                    keypairs_orgs = __get_keypairs(o, reqs[i], keypairs_orgs)
        (keyvals, reidentify) = __reidentifying_pairs(fw, keypairs_orgs, n,
                                                      control_kp, filter)
        if len(keyvals) > 0:
            kp_all[n] = keyvals
        reident_all[n] = reidentify
    # better only on debug mode
    print_json(fw, kp_all)
    return reident_all


def measure_samekey_difforigin(args: Args) -> None:
    fp: Fpointers = prepare_output(args.input.name, args.format)
    input_graph: MultiDiGraph = read_gpickle(args.input.name)
    control_graph: Optional[MultiDiGraph] = None
    ctrl_reidentifying_kp: Optional[ReidentifyingOrgs_all] = None
    if args.control:
        control_graph = read_gpickle(args.control.name)
        print("Processing graph from", args.control.name)
        ctrl_reidentifying_kp = __process_graph(None, control_graph, None,
                                                args.filters)
    print("Processing graph from", args.input.name)
    reidentifying_kp = __process_graph(fp, input_graph, ctrl_reidentifying_kp,
                                       args.filters)
    print_reidentification(fp, reidentifying_kp)
    closeFiles(fp)
