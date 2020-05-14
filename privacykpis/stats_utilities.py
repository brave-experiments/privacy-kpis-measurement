from typing import TextIO, Dict, List, Optional, Tuple, Any
import networkx  # type: ignore
from networkx import MultiDiGraph
import numpy  # type: ignore
import json


KeyPairsOrigins = Dict[str, List[Dict[str, Any]]]
ReidentifyingOrgs = Dict[str, Dict[str, Dict[str, Any]]]
Fpointers = Dict[str, TextIO]
DL = "\t"


def get_origins(input_graph: MultiDiGraph) -> List[str]:
    initOrigins = []
    for n, d in list(input_graph.nodes(data=True)):
        # not sure why but there is None site in the trace
        if n is None or d is None:
            print("Something wrong happened? Node:", n, d)
            continue
        if d["type"] == "site":
            initOrigins.append(n)
    return initOrigins


def print_json(fw: Optional[Fpointers], kp_all: KeyPairsOrigins) -> None:
    if fw is not None and "kp_json" in fw:
        fw["kp_json"].write(json.dumps(kp_all))


def __get_filename(inputFile: str) -> str:
    if "." in inputFile:
        parts = inputFile.split(".")
        return parts[0]
    return inputFile


def print_reidentification(fw: Optional[Fpointers], reidentify:
                           ReidentifyingOrgs, tp: str) -> None:
    count = 0
    for k in reidentify:
        for v in reidentify[k]:
            numSites = len(numpy.unique(reidentify[k][v]["origins"]))
            if numSites > 1:
                if fw is not None and "rid_ver_tsv" in fw:
                    fw["rid_ver_tsv"].write(tp+DL+k+DL+v+DL+str(numSites)+DL +
                                            reidentify[k][v]["token_type"] +
                                            "\n")
                count += numSites
    if fw is not None and "rid_tsv" in fw:
        fw["rid_tsv"].write(tp+"\t"+str(count)+"\n")


def print_KeyPair(fw: Optional[Fpointers], tp: str, k: str, v: str, origin:
                  str, token_type: str, timestamp: str) -> None:
    if fw is not None and "kp_tsv" in fw:
        fw["kp_tsv"].write(tp+DL+k+DL+v+DL+origin+DL+token_type+DL +
                           timestamp+"\n")


def prepare_output(inputFilename: str, outformat: str) -> Fpointers:
    filename = __get_filename(inputFilename)
    fw: Fpointers = {}
    if "tsv" in outformat:
        fw["kp_tsv"] = open(f'{filename}_keypairs.tsv', "w")
        fw["kp_tsv"].write(f'tpDomain{DL}key{DL}value{DL}origin{DL}token_typ' +
                           'e{DL}timestamp\n')
        fw["rid_ver_tsv"] = open(filename+"_reidentification_verbose.tsv", "w")
        fw["rid_ver_tsv"].write(f'tpDomain{DL}key{DL}value{DL}sites_reident' +
                                'ifies{DL}token_type\n')
        fw["rid_tsv"] = open(f'{filename}_reidentification.tsv', "w")
        fw["rid_tsv"].write(f'tpDomain{DL}num_of_sites_reidentifies\n')
    else:
        fw["kp_json"] = open(f'{filename}_keypairs.json', "w")
    return fw


def closeFiles(files: Optional[Fpointers]) -> None:
    if files is None:
        return
    for k in files:
        if files[k] is not None:
            files[k].close
