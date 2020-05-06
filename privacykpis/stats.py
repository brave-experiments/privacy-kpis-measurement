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

def get_origins(input_graph):
    initOrigins=[]
    for n, d in list(input_graph.nodes(data=True)):
        # not sure why but there is None site in the trace
        if n == None or d == None:
            print("Something wrong happened? "+str(n)+" "+str(d))
            continue
        if d["type"] == "site":
            initOrigins.append(n)
    return initOrigins

def get_params_edge(input_graph,o,n):
    params_from_origin=[]
    reqs = input_graph.get_edge_data(o, n)
    for i in reqs:
        params = reqs[i]["query tokens"]
        if params != None:
            params_from_origin+=params
    print("EDGE",o,n,len(params_from_origin))
    return params_from_origin

def compare_pairs(prev_pairs,cur_pairs,cur):
    same_pairs = {}
    print(len(cur_pairs),len(prev_pairs))
    for p in prev_pairs:
        for c in cur_pairs:
            if p == c:
                print(cur,"has same pair: ", same_pairs, "with", p)
    return same_pairs

def measure_samekey_difforigin(args: Args):
    input_graph: networkx.MultiDiGraph = read_gpickle(args.input.name)
    control_graph: Optional[networkx.MultiDiGraph]
    if args.control:
        control_graph = read_gpickle(args.control)
    else:
        args.control = None
    origins = get_origins(input_graph)
    for n, d in list(input_graph.nodes(data=True)):
        # get 3party only 
        if  n == None or d["type"] == "site":
            continue
        if n != "gstatic.com":
            print("done",n)
            import sys;sys.exit() 
        params_from_all_origins={}
        for o in input_graph.predecessors(n):
            # check edge with origin
            if o in origins and (o, n) in input_graph.edges:
                this_origin = get_params_edge(input_graph,o,n)
                if len(this_origin) == 0:
                    continue
                compare_pairs(params_from_all_origins,this_origin,o) 
                params_from_all_origins[o] += this_origin 