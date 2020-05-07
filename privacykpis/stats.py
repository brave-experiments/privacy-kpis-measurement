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


KeyPairsOrigins = Dict[Tuple[str, str], List[Any]]

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


def compare_pairs(fw: TextIO, prev_qtokens: KeyPairsOrigins,
                  tp: str) -> List[Dict[str, Any]]:
    keyvals = []
    for pp in prev_qtokens:
        if len(prev_qtokens[pp]) > 1:
            for arr in prev_qtokens[pp]:
                k, v = pp
                fw.write(tp+"\t"+k+"\t"+v+"\t"+arr[0]+"\t"+str(arr[1]) +
                            "\t"+arr[2]+"\n")
                keyvals.append({"key": k, "val": v, "origin": arr[0],
                                "cookies": arr[1], "timestamp": arr[2]})
    return keyvals


def measure_samekey_difforigin(args: Args) -> None:
    filename = args.input.name.split(".")[0]
    input_graph: MultiDiGraph = read_gpickle(args.input.name)
    control_graph: Optional[MultiDiGraph] = None
    results = {}
    if args.control:
        control_graph = read_gpickle(args.control)
    origins = get_origins(input_graph)
    fw = open(filename+"_results.tsv", "w")
    fw.write("third party\tkey\tvalue\torigin\tcookies\ttimestamp\n")
    for n, d in list(input_graph.nodes(data=True)):
        # get 3party only
        if n is None or d["type"] == "site":
            continue
        params_all_origins: KeyPairsOrigins = {}
        for o in input_graph.predecessors(n):
            # check edge with origin
            if o in origins and (o, n) in input_graph.edges:
                reqs = input_graph.get_edge_data(o, n)
                for i in reqs:
                    if reqs[i]["query tokens"] is None:
                        continue
                    # get qtokens for all origins associated with this 3party
                    for pp in reqs[i]["query tokens"]:
                        cookies = reqs[i]["cookies tokens"]
                        timestamp = reqs[i]["timestamp"]
                        if pp not in params_all_origins:
                            params_all_origins[pp] = []
                        params_all_origins[pp].append([o, cookies, timestamp])
        temp = compare_pairs(fw, params_all_origins, n)
        if len(temp) > 0:
            results[n] = temp
    fw.close
    with open(filename+"_results.json", "w") as fw:
        fw.write(json.dumps(results))
