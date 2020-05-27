import csv
import json
from typing import Any, cast, Dict, List, Optional, TextIO, Tuple, Union

import networkx  # type: ignore
from networkx import MultiDiGraph
import warnings

import privacykpis.common
from privacykpis.tokenizing import TokenLocation, TokenKey, TokenValue
from privacykpis.consts import TOKEN_LOCATION, ORIGIN, TIMESTAMP
from privacykpis.consts import KEY, VALUE, TYPE, SITE
from privacykpis.types import CSVWriter, RequestRec

KeyPairsOrigins = Dict[str, List[RequestRec]]
ReidentifyingOrgs = Dict[str, Dict[str, Dict[str, Any]]]
ReidentifyingOrgsAll = Dict[str, ReidentifyingOrgs]
ReportOutput = Union[privacykpis.types.CSVWriter, TextIO]
ReportWriters = Dict[str, ReportOutput]


def get_origins(input_graph: MultiDiGraph) -> List[str]:
    init_origins = []
    for n, d in input_graph.nodes(data=True):
        if d[TYPE] == SITE:
            init_origins.append(n)
    return init_origins


def print_json(writer: TextIO,
               kp_all: KeyPairsOrigins) -> None:
    writer.write(json.dumps(kp_all))


def get_filename(file_name: str) -> str:
    if "." in file_name:
        parts = file_name.split(".")
        return parts[0]
    return file_name


def print_keypair(writer: CSVWriter, tp: str,
                  key: TokenKey, value: TokenValue, origin: str,
                  token_loc: TokenLocation, timestamp: str) -> None:
    row = [tp, key, value, origin, token_loc.name, timestamp]
    writer.writerow(row)


def csv_writer(filename: str, headers: List[str]) -> CSVWriter:
    handle = open(f"{filename}.csv", "w")
    writer = csv.writer(handle)
    writer.writerow(headers)
    return cast(CSVWriter, writer)


def prepare_output(fname: str, outformat: str, debug: bool
                   ) -> Tuple[ReportWriters, ReportWriters]:
    base = get_filename(fname)
    writers: ReportWriters = {}
    writersc: ReportWriters = {}
    if debug:
        keypairs_headers = ["tpDomain", KEY, VALUE, ORIGIN, TOKEN_LOCATION,
                            TIMESTAMP]
        writers["kp_csv"] = csv_writer(f"{base}_keypairs", keypairs_headers)
    if "csv" in outformat:
        ver_csv_headers = ["tpDomain", KEY, VALUE, "sites_reidentifies",
                           TOKEN_LOCATION]
        writers["rid_ver_csv"] = csv_writer(f"{base}_reidentification_verbose",
                                            ver_csv_headers)
        rid_csv_headers = ["tpDomain", "num_of_sites_reidentifies"]
        writers["rid_csv"] = csv_writer(f"{base}_reidentification",
                                        rid_csv_headers)
    else:
        writers["rid_ver_json"] = open(f"{base}_reidentification_verbose.json",
                                       "w")
        writers["rid_json"] = open(f"{base}_reidentification.json", "w")
    return (writers, writersc)


def print_reidentification(fw: ReportWriters,
                           reidentify_all: ReidentifyingOrgsAll) -> None:
    rid_sum = {}
    printer_json: Dict[str, Any] = {}
    rid_ver_writer = cast(CSVWriter,
                          fw["rid_ver_csv"]) if "rid_ver_csv" in fw else None
    rid_writer = cast(CSVWriter, fw["rid_csv"]) if "rid_csv" in fw else None
    json_ver_writer = fw["rid_ver_json"] if "rid_ver_json" in fw else None
    rid_json_writer = fw["rid_json"] if "rid_json" in fw else None

    for tp in sorted(reidentify_all.keys()):
        tp_reID = reidentify_all[tp]
        count = 0
        for k in tp_reID:
            for v in tp_reID[k]:
                num_sites = len(set(tp_reID[k][v][ORIGIN]))
                if num_sites > 1:
                    tk_loc: TokenLocation = tp_reID[k][v][TOKEN_LOCATION]
                    # json case
                    if json_ver_writer:
                        if tp not in printer_json:
                            printer_json[tp] = []
                        printer_json[tp].append({KEY: k, VALUE: v,
                                                TOKEN_LOCATION: tk_loc.name,
                                                 "sites_reidentifies":
                                                 num_sites})
                    # csv case
                    if rid_ver_writer:
                        row = [tp, k, v, str(num_sites), tk_loc.name]
                        rid_ver_writer.writerow(row)
                    count += num_sites
        if rid_writer:
            rid_writer.writerow([tp, str(count)])
        rid_sum[tp] = {"num_of_sites_reidentifies": count}
    # json case
    if json_ver_writer:
        cast(TextIO, json_ver_writer).write(json.dumps(printer_json))
    if rid_json_writer:
        cast(TextIO, rid_json_writer).write(json.dumps(rid_sum))
