import argparse
import pickle
import networkx  # type: ignore
from networkx import MultiDiGraph, read_gpickle
from typing import TextIO, Dict, List, Optional, Tuple, Any
import privacykpis.args
from privacykpis.stats_utilities import *


class Args(privacykpis.args.Args):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.input = args.input
        self.control = args.control
        self.format = args.format
        self.is_valid = True


FORMATS = {"tsv", "json"}


def __reidentifying_pairs(fw: Optional[Fpointers], ptokens: KeyPairsOrigins,
                          tp: str, control_kp: Optional[KeyPairsOrigins]
                          ) -> Tuple[List[Dict[str, Any]], ReidentifyingOrgs]:
    keyvals = []
    reidentify: ReidentifyingOrgs = {}
    for k in ptokens:
        for obj in ptokens[k]:
            v = obj["val"]
            print_KeyPair(fw, tp, k, v, obj["origin"], obj["token_type"],
                          obj["timestamp"])
            keyvals.append({"key": k, "token_type": obj["token_type"],
                            "timestamp": obj["timestamp"], "val": v,
                            "origin": obj["origin"]})
            if k not in reidentify:
                reidentify[k] = {}
            if v not in reidentify[k]:
                reidentify[k][v] = {"origins": [], "token_type": str}
            reidentify[k][v]["origins"].append(obj["origin"])
            reidentify[k][v]["token_type"] = obj["token_type"]
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
                    Optional[KeyPairsOrigins]) -> KeyPairsOrigins:
    origins = get_origins(graph)
    kp_all = {}
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
                                                      control_kp)
        print_reidentification(fw, reidentify, n)
        if len(keyvals) > 0:
            kp_all[n] = keyvals
    return kp_all


def measure_samekey_difforigin(args: Args) -> None:
    fp: Fpointers = prepare_output(args.input.name, args.format)
    input_graph: MultiDiGraph = read_gpickle(args.input.name)
    control_graph: Optional[MultiDiGraph] = None
    control_kp_all: Optional[KeyPairsOrigins] = None
    if args.control:
        control_graph = read_gpickle(args.control.name)
        print("Processing graph from", args.control.name)
        control_kp_all = __process_graph(None, control_graph, None)
    print("Processing graph from", args.input.name)
    kp_all = __process_graph(fp, input_graph, control_kp_all)
    print_json(fp, kp_all)
    closeFiles(fp)
