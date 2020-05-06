import argparse
import pickle
from typing import Optional
from networkx import MultiDiGraph
from networkx import read_gpickle
import json
import privacykpis.args


class Args(privacykpis.args.Args):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.input = args.input
        self.control = args.control
        self.is_valid = True


def requested_sites_subgraphs(graph: MultiDiGraph):
    pass

def get_origins(input_graph: MultiDiGraph):
    initOrigins=[]
    for n, d in list(input_graph.nodes(data=True)):
        # not sure why but there is None site in the trace
        if n == None or d == None:
            print("Something wrong happened? Node: "+str(n)+" "+str(d))
            continue
        if d["type"] == "site":
            initOrigins.append(n)
    return initOrigins

def compare_pairs(fw,prev_qtokens:dict,tp:str) -> dict:
    params = {}
    for pp in prev_qtokens:
        if len(prev_qtokens[pp])>1:
            for arr in prev_qtokens[pp]:
                fw.write(tp+"\t"+str(pp)+"\t"+arr[0]+"\t"+str(arr[1])+"\t"+arr[2]+"\n")
                if str(pp) not in params:
                    params[str(pp)] = []
                params[str(pp)].append({"origin":arr[0],"cookies":arr[1],"timestamp":arr[2]})
            return {"query_tokens": params}
    return None

def measure_samekey_difforigin(args: Args):
    filename = args.input.name.split(".")[0]
    input_graph: MultiDiGraph = read_gpickle(args.input.name)
    control_graph: Optional[MultiDiGraph] = None
    results = {}
    if args.control:
        control_graph = read_gpickle(args.control)
    origins = get_origins(input_graph)
    fw=open(filename+"_results.tsv","w")
    fw.write("third party\tquery token\torigin\tcookies\ttimestamp\n")
    for n, d in list(input_graph.nodes(data=True)):
        # get 3party only
        if  n == None or d["type"] == "site":
            continue     
        params_from_all_origins={}
        for o in input_graph.predecessors(n):
            # check edge with origin
            if o in origins and (o, n) in input_graph.edges:
                reqs = input_graph.get_edge_data(o, n)
                for i in reqs:
                    if reqs[i]["query tokens"] == None:
                        continue
                    #get qtokens for all origins associated to this 3party
                    for pp in reqs[i]["query tokens"]:
                        cookies = reqs[i]["cookies tokens"]
                        timestamp = reqs[i]["timestamp"]
                        if pp not in params_from_all_origins:
                            params_from_all_origins[pp]=[]
                        params_from_all_origins[pp].append([o,cookies,timestamp])
        temp = compare_pairs(fw,params_from_all_origins,n)
        if temp != None:
            results[n] = temp
    fw.close
    with open(filename+"_results.json","w") as fw:
        fw.write(json.dumps(results))
    print(len(results))