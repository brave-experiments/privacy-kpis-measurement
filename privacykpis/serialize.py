import argparse
import base64
import datetime
import json
import pathlib
from urllib.parse import urlparse

import networkx
from networkx import MultiDiGraph
from publicsuffixlist import PublicSuffixList

import privacykpis.args
import privacykpis.tokenizing


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
                measurement = SiteMeasurement(json.loads(line))
                measurement.add_to_graph(graph)
        else:
            measurement = SiteMeasurement(json.load(input_file))
            measurement.add_to_graph(graph)
    return graph


class SiteMeasurement:
    def __init__(self, record: dict):
        self.start_timestamp = datetime.datetime.fromisoformat(record["start"])
        self.end_timestamp = datetime.datetime.fromisoformat(record["end"])
        self.url = record["url"]
        self.parsed_url = urlparse(record["url"])
        self.records = [Request(r) for r in record["requests"]]

    def add_to_graph(self, graph: MultiDiGraph):
        graph.add_node(self.url, type="site")
        for record in self.records:
            record.add_to_graph(self, graph)


class Request:
    """Represents a single request made by the browser.

    Args:
    record -- a request, as recorded by record.py
    """
    psl = PublicSuffixList()

    def __init__(self, record: dict):
        tokens = privacykpis.tokenizing.from_record(record)
        self.cookie_tokens = tokens["cookies"]
        self.path_tokens = tokens["path"]
        self.query_tokens = tokens["query"]
        self.body_tokens = tokens["body"]
        self.body_encoding = tokens["body encoding"]
        self.parsed_url = urlparse(record["url"])
        self.url = record["url"]
        self.etld_pone = self.psl.privatesuffix(self.parsed_url.netloc)
        self.timestamp = datetime.datetime.fromisoformat(record["time"])

    def add_to_graph(self, site: SiteMeasurement, graph: MultiDiGraph):
        graph.add_node(self.etld_pone, type="requested etld+1")
        graph.add_edge(site.url, self.etld_pone, **{
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "cookies tokens": self.cookie_tokens,
            "path tokens": self.path_tokens,
            "query tokens": self.query_tokens,
            "body tokens": self.body_tokens,
        })


def graphml_preprocess(from_graph: MultiDiGraph) -> MultiDiGraph:
    to_graph = MultiDiGraph()

    for n, d in from_graph.nodes.data():
        to_graph.add_node(n, **d)

    token_keys = ["cookies", "path", "query", "body"]

    for u, v, index, d in from_graph.edges(data=True, keys=True):
        edge_data = {
            "url": d["url"],
            "timestamp": d["timestamp"],
        }
        for key_prefix in token_keys:
            key_name = f"{key_prefix} tokens"
            token_values = d[key_name]
            if not token_values:
                continue
            for k, v in token_values:
                edge_data_key = f"{key_prefix}:{k}"
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
