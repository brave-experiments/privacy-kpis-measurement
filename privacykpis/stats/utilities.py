import csv
import json
from typing import Any, cast, Dict, List, Optional, TextIO, Tuple, Union

import networkx  # type: ignore
from networkx import MultiDiGraph
import warnings

import privacykpis.common
from privacykpis.tokenizing import TokenLocation, TokenKey, TokenValue
from privacykpis.consts import TOKEN_LOCATION, ORIGIN, TIMESTAMP
from privacykpis.consts import TOKEN_KEY, TOKEN_VALUE, NODE_TYPE, SITE
from privacykpis.types import CSVWriter, RequestRec

ReidentifyingPairs = Dict[TokenKey, Dict[TokenValue, Dict[str, Any]]]
ReportOutput = Union[privacykpis.types.CSVWriter, TextIO]
ReportWriters = Dict[str, ReportOutput]


def get_origins(input_graph: MultiDiGraph) -> List[str]:
    init_origins = []
    for n, d in input_graph.nodes(data=True):
        if d[NODE_TYPE] == SITE:
            init_origins.append(n)
    return init_origins


def __get_filename(file_name: str) -> str:
    if "." in file_name:
        parts = file_name.split(".")
        return parts[0]
    return file_name


def csv_writer(filename: str, headers: List[str]) -> CSVWriter:
    handle = open(f"{filename}.csv", "w")
    writer = cast(CSVWriter, csv.writer(handle))
    print_to_csv(writer, headers)
    return writer


def prepare_output(fname: str, outformat: str, debug: bool
                   ) -> Tuple[ReportWriters, ReportWriters]:
    base = __get_filename(fname)
    writers: ReportWriters = {}
    writersc: ReportWriters = {}
    if debug:
        keypairs_headers = ["tpDomain", TOKEN_KEY, TOKEN_VALUE,
                            ORIGIN, TOKEN_LOCATION, TIMESTAMP]
        writers["kp_csv"] = csv_writer(f"{base}_keypairs", keypairs_headers)
    if "csv" in outformat:
        ver_csv_headers = ["tpDomain", TOKEN_KEY, TOKEN_VALUE,
                           "sites_reidentifies", TOKEN_LOCATION]
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


def print_reidentifiying_tokens(fw: ReportWriters, reidentify_all: Dict[str,
                                ReidentifyingPairs]) -> None:
    rid_sum = {}
    printer_json: Dict[str, Any] = {}
    csv_ver_writer = cast(CSVWriter,
                          fw["rid_ver_csv"]) if "rid_ver_csv" in fw else None
    csv_writer = cast(CSVWriter, fw["rid_csv"]) if "rid_csv" in fw else None
    json_ver_writer = cast(TextIO, fw["rid_ver_json"]) if ("rid_ver_json" in
                                                           fw) else None
    json_writer = cast(TextIO, fw["rid_json"]) if "rid_json" in fw else None

    for tparty in sorted(reidentify_all.keys()):
        tp_reID = reidentify_all[tparty]
        total_sites = 0
        for token_k in tp_reID:
            for token_v in tp_reID[token_k]:
                num_sites = len(set(tp_reID[token_k][token_v][ORIGIN]))
                if num_sites <= 1:
                    continue
                tk_loc: TokenLocation = tp_reID[token_k][token_v][
                                        TOKEN_LOCATION]
                # json case
                if json_ver_writer:
                    printer_json = __make_json_entry(tparty, printer_json,
                                                     token_k, token_v,
                                                     tk_loc, num_sites)
                # csv case
                if csv_ver_writer:
                    row = [tparty, token_k, token_v,
                           str(num_sites), tk_loc.name]
                    print_to_csv(csv_ver_writer, row)
                total_sites += num_sites
        if csv_writer:
            print_to_csv(csv_writer, [tparty, str(total_sites)])
        rid_sum[tparty] = {"num_of_sites_reidentifies": total_sites}
    # json case
    if json_ver_writer:
        print_to_json(json_ver_writer, printer_json)
    if json_writer:
        print_to_json(json_writer, rid_sum)


def __make_json_entry(tparty: str, printer_json: Dict[str, Any],
                      token_k: TokenKey, token_v: TokenValue, tk_loc:
                      TokenLocation, num_sites: int) -> Dict[str, Any]:
    if tparty not in printer_json:
        printer_json[tparty] = []
    entry = {TOKEN_KEY: token_k, TOKEN_VALUE: token_v,
             TOKEN_LOCATION: tk_loc.name, "sites_reidentifies": num_sites}
    printer_json[tparty].append(entry)
    return printer_json


def print_to_csv(out: CSVWriter, data: List[str]) -> None:
    out.writerow(data)


def print_to_json(out: TextIO, data: Dict[str, Any]) -> None:
    out.write(json.dumps(data))
