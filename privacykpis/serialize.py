import argparse
import base64
import datetime
import json
import pathlib
from typing import Any, Dict
from urllib.parse import urlparse

import networkx  # type: ignore
from networkx import MultiDiGraph
from publicsuffixlist import PublicSuffixList  # type: ignore

import privacykpis.args
from privacykpis.tokenizing import TokenLocation
from privacykpis.consts import TIMESTAMP, URL, REQUESTED_ETLD1, SITE

RawRecord = Dict[str, Any]


class Args(privacykpis.args.Args):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.is_valid = True
        self.input = args.input
        self.multi = args.multi
        self.output = args.output
        self.format = args.format


def graph_from_args(args: Args) -> MultiDiGraph:
    graph = MultiDiGraph()
    for input_file in args.input:
        if args.multi:
            for line in input_file:
                if line.strip() == "":
                    continue
                measurement = SiteMeasurement(json.loads(line))
                measurement.add_to_graph(graph)
        else:
            measurement = SiteMeasurement(json.load(input_file))
            measurement.add_to_graph(graph)
    return graph


class SiteMeasurement:
    def __init__(self, record: RawRecord) -> None:
        self.start_timestamp = datetime.datetime.fromisoformat(record["start"])
        self.end_timestamp = datetime.datetime.fromisoformat(record["end"])
        self.url = record[URL]
        self.parsed_url = urlparse(record[URL])
        self.records = [Request(r) for r in record["requests"]]

    def add_to_graph(self, graph: MultiDiGraph) -> None:
        graph.add_node(self.url, type=SITE)
        for record in self.records:
            record.add_to_graph(self, graph)


class Request:
    """Represents a single request made by the browser.

    Args:
    record -- a request, as recorded by record.py
    """
    psl = PublicSuffixList()

    def __init__(self, record: RawRecord) -> None:
        tokens = privacykpis.tokenizing.from_record(record)
        self.cookie_tokens = tokens.cookies
        self.path_tokens = tokens.path
        self.query_tokens = tokens.query
        self.body_tokens = tokens.body
        self.body_encoding = tokens.body_encoding
        self.parsed_url = urlparse(record[URL])
        self.url = record[URL]
        self.etld_pone = self.psl.privatesuffix(self.parsed_url.netloc)
        self.timestamp = datetime.datetime.fromisoformat(record["time"])

    def add_to_graph(self, site: SiteMeasurement, graph: MultiDiGraph) -> None:
        graph.add_node(self.etld_pone, type=REQUESTED_ETLD1)
        graph.add_edge(site.url, self.etld_pone, **{
            URL: self.url,
            TIMESTAMP: self.timestamp.isoformat(),
            TokenLocation.COOKIE.name: self.cookie_tokens,
            TokenLocation.PATH.name: self.path_tokens,
            TokenLocation.QUERY_PARAM.name: self.query_tokens,
            TokenLocation.BODY.name: self.body_tokens,
        })


def graphml_preprocess(from_graph: MultiDiGraph) -> MultiDiGraph:
    to_graph = MultiDiGraph()

    for n, d in from_graph.nodes.data():
        to_graph.add_node(n, **d)

    for u, v, index, d in from_graph.edges(data=True, keys=True):
        edge_data = {
            URL: d[URL],
            TIMESTAMP: d[TIMESTAMP],
        }
        for location in TokenLocation:
            token_values = d[location]
            if not token_values:
                continue
            for k, v in token_values:
                edge_data_key = f"{location}:{k}"
                edge_data[edge_data_key] = v
        to_graph.add_edge(u, v, key=index)
        to_graph.edges[u, v, index].update(edge_data)
    return to_graph


def pickle_preprocess(graph: MultiDiGraph) -> MultiDiGraph:
    return graph


FORMATS = {
    "graphml": (graphml_preprocess, networkx.write_graphml),
    "pickle": (pickle_preprocess, networkx.write_gpickle),
}
