from typing import TextIO, Dict, List, Optional, Tuple, Any
import networkx  # type: ignore
from networkx import MultiDiGraph
import numpy  # type: ignore
import json
import argparse

KeyPairsOrigins = Dict[str, List[Dict[str, Any]]]
ReidentifyingOrgs = Dict[str, Dict[str, Dict[str, Any]]]
ReidentifyingOrgs_all = Dict[str, ReidentifyingOrgs]
Fpointers = Dict[str, TextIO]
DL = "\t"


def check_positive(value: str) -> int:
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(value+" is an invalid " +
                                         "positive int value")
    return ivalue


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


def print_reidentification(fw: Optional[Fpointers], reidentify_all:
                           ReidentifyingOrgs_all) -> None:
    rid_sum = {}
    printer_json: Dict[str, Any] = {}
    for tp in sorted(reidentify_all.keys()):
        tp_reidentify = reidentify_all[tp]
        count = 0
        for k in tp_reidentify:
            for v in tp_reidentify[k]:
                nSites = len(numpy.unique(tp_reidentify[k][v]["origins"]))
                if nSites > 1:
                    ttype = tp_reidentify[k][v]["token_type"]
                    # json case
                    if fw is not None and "rid_ver_json" in fw:
                        if tp not in printer_json:
                            printer_json[tp] = []
                        printer_json[tp].append({"key": k, "value": v,
                                                 "token_type": ttype,
                                                 "sites_reidentifies":
                                                 nSites})
                    # tsv case
                    if fw is not None and "rid_ver_tsv" in fw:
                        fw["rid_ver_tsv"].write(tp+DL+k+DL+v+DL+str(nSites) +
                                                DL+ttype+"\n")
                    count += nSites
        if fw is not None and "rid_tsv" in fw:
            fw["rid_tsv"].write(tp+"\t"+str(count)+"\n")
        rid_sum[tp] = {"num_of_sites_reidentifies": count}
    # json case
    if fw is not None and "rid_ver_json" in fw:
        fw["rid_ver_json"].write(json.dumps(printer_json))
    if fw is not None and "rid_json" in fw:
        fw["rid_json"].write(json.dumps(rid_sum))


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
                           f'e{DL}timestamp\n')
        fw["rid_ver_tsv"] = open(filename+"_reidentification_verbose.tsv", "w")
        fw["rid_ver_tsv"].write(f'tpDomain{DL}key{DL}value{DL}sites_reident' +
                                f'ifies{DL}token_type\n')
        fw["rid_tsv"] = open(f'{filename}_reidentification.tsv', "w")
        fw["rid_tsv"].write(f'tpDomain{DL}num_of_sites_reidentifies\n')
    else:
        fw["kp_json"] = open(f'{filename}_keypairs.json', "w")
        fw["rid_ver_json"] = open(filename+"_reidentification_verbose.json",
                                  "w")
        fw["rid_json"] = open(f'{filename}_reidentification.json', "w")
    return fw


def closeFiles(files: Optional[Fpointers]) -> None:
    if files is None:
        return
    for k in files:
        if files[k] is not None:
            files[k].close


def kp_exists_in_control(control_reid_all: Optional[ReidentifyingOrgs_all],
                         this_tp: str,  this_k: str, this_v: str,
                         this_org: str, this_ttype: str) -> bool:
    if control_reid_all is None or this_tp not in control_reid_all:
        return False
    ctrl_kp = control_reid_all[this_tp]
    if (this_k in ctrl_kp) and (this_v in ctrl_kp[this_k] and ctrl_kp
                                [this_k][this_v]["token_type"] == this_ttype
                                and this_org in ctrl_kp[this_k][this_v]
                                ["origins"]):
        return True
    return False
