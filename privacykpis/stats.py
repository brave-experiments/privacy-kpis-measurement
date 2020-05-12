import argparse
import pickle
import networkx  # type: ignore
from networkx import MultiDiGraph, read_gpickle
import json
from typing import TextIO, Dict, List, Optional, Tuple, Any

import privacykpis.args


class Args(privacykpis.args.Args):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.input = args.input
        self.control = args.control
        self.is_valid = True


KeyPairsOrigins = Dict[str, List[Dict[str, Any]]]

# def requested_sites_subgraphs(graph: MultiDiGraph):
#    pass


def get_origins(input_graph: MultiDiGraph) -> List[str]:
    initOrigins = []
    for n, d in list(input_graph.nodes(data=True)):
        # not sure why but there is None site in the trace
        if n is None or d is None:
            print("Something wrong happened? Node: "+str(n)+" "+str(d))
            continue
        if d["type"] == "site":
            initOrigins.append(n)
    return initOrigins


def compare_and_print(fw: TextIO, prev_qtokens: KeyPairsOrigins,
                      tp: str) -> List[Dict[str, Any]]:
    keyvals = []
    for k in prev_qtokens:
        if len(prev_qtokens[k]) > 1:
            for obj in prev_qtokens[k]:
                fw.write(tp+"\t"+k+"\t"+obj["val"]+"\t"+obj["origin"] +
                         "\t"+obj["type"]+"\t"+obj["timestamp"]+"\n")
                keyvals.append({"key": k, "val": obj["val"],
                                "origin": obj["origin"], "type": obj["type"],
                                "timestamp": obj["timestamp"]})
    return keyvals


def get_keypairs(o: str, req: Dict[str, Any],
                 kpairs: KeyPairsOrigins) -> KeyPairsOrigins:
    kpairs = demul_token(o, req, "query tokens", kpairs)
    kpairs = demul_token(o, req, "cookies tokens", kpairs)
    kpairs = demul_token(o, req, "path tokens", kpairs)
    kpairs = demul_token(o, req, "body tokens", kpairs)
    return kpairs


def demul_token(o: str, req: Dict[str, Any], token_type: str,
                kpairs: KeyPairsOrigins) -> KeyPairsOrigins:
    tokens = req[token_type]
    if tokens is None:
        return kpairs
    for (k, v) in tokens:
        if k not in kpairs:
            kpairs[k] = []
        kpairs[k].append({"origin": o, "val": v, "type": token_type,
                         "timestamp": req["timestamp"]})
    return kpairs


def measure_samekey_difforigin(args: Args) -> None:
    filename = args.input.name.split(".")[0]
    input_graph: MultiDiGraph = read_gpickle(args.input.name)
    control_graph: Optional[MultiDiGraph] = None
    results = {}
    if args.control:
        control_graph = read_gpickle(args.control)
    origins = get_origins(input_graph)
    fw = open(filename+"_results.tsv", "w")
    fw.write("third party\tkey\tvalue\torigin\ttype\ttimestamp\n")
    for n, d in list(input_graph.nodes(data=True)):
        # get 3party only
        if n is None or d["type"] == "site":
            continue
        keypairs_orgs: KeyPairsOrigins = {}
        for o in input_graph.predecessors(n):
            # check edge with origin
            if o in origins and (o, n) in input_graph.edges:
                reqs = input_graph.get_edge_data(o, n)
                for i in reqs:
                    # get tokens for all origins associated with this 3party
                    keypairs_orgs = get_keypairs(o, reqs[i], keypairs_orgs)
        temp = compare_and_print(fw, keypairs_orgs, n)
        if len(temp) > 0:
            results[n] = temp
    fw.close
    with open(filename+"_results.json", "w") as fw:
        fw.write(json.dumps(results))
