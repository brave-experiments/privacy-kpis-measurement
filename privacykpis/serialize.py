import argparse
import datetime
import json
import pathlib
import pickle
import sys
from typing import cast, Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

import networkx  # type: ignore
from networkx import MultiDiGraph
from publicsuffixlist import PublicSuffixList  # type: ignore

import privacykpis.args
from privacykpis.consts import TIMESTAMP, URL, REQUESTED_ETLD1, SITE
from privacykpis.redirects import RedirectCache
import privacykpis.tokenizing
from privacykpis.types import Domain, ThirdPartyDomain, FirstPartyDomain, Token
from privacykpis.types import TokenLocation, ISOTimestamp, RequestTimestamp


PSL = PublicSuffixList()

RawRecord = Dict[str, Any]
FirstPartyIdentifications = Dict[FirstPartyDomain, List[RequestTimestamp]]
TokenIdentifications = Dict[Token, FirstPartyIdentifications]
TrackingTokenCollection = Dict[ThirdPartyDomain, TokenIdentifications]


class Args(privacykpis.args.Args):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.is_valid = True
        self.input = args.input
        self.multi = args.multi
        self.output = args.output
        self.debug = args.debug
        self.redirect_cache_path = args.redirect_cache


class SiteMeasurement:
    redirect_cache: RedirectCache

    def __init__(self, record: RawRecord, redirect_cache: RedirectCache,
                 debug: bool = False) -> None:
        self.start_timestamp = datetime.datetime.fromisoformat(record["start"])
        self.end_timestamp = datetime.datetime.fromisoformat(record["end"])
        self.url = record[URL]
        self.parsed_url = urlparse(record[URL])
        self.etld_pone = PSL.privatesuffix(self.parsed_url.netloc)
        self.records = [Request(r) for r in record["requests"]]
        self.debug = debug
        self.redirect_cache = redirect_cache

    def add_to_graph(self, graph: MultiDiGraph) -> None:
        if self.redirect_cache.is_redirect(self.url):
            if self.debug:
                print(f"Skipping {self.url}, looks like it redirects.")
            return
        graph.add_node(self.url, type=SITE)
        for record in self.records:
            record.add_to_graph(self, graph)


class Request:
    """Represents a single request made by the browser.

    Args:
    record -- a request, as recorded by record.py
    """
    def __init__(self, record: RawRecord) -> None:
        tokens = privacykpis.tokenizing.from_record(record)
        self.cookie_tokens = tokens.cookies
        self.path_tokens = tokens.path
        self.query_tokens = tokens.query
        self.body_tokens = tokens.body
        self.body_encoding = tokens.body_encoding
        self.parsed_url = urlparse(record[URL])
        self.url = record[URL]
        self.etld_pone = PSL.privatesuffix(self.parsed_url.netloc)
        self.timestamp = datetime.datetime.fromisoformat(record["time"])

    def add_to_graph(self, site: SiteMeasurement, graph: MultiDiGraph) -> None:
        graph.add_node(self.etld_pone, type=REQUESTED_ETLD1)
        graph.add_edge(site.etld_pone, self.etld_pone, **{
            URL: self.url,
            TIMESTAMP: self.timestamp.isoformat(),
            TokenLocation.COOKIE.name: self.cookie_tokens,
            TokenLocation.PATH.name: self.path_tokens,
            TokenLocation.QUERY_PARAM.name: self.query_tokens,
            TokenLocation.BODY.name: self.body_tokens,
        })


class TrackingInstances:
    token_collection: TrackingTokenCollection = {}

    @staticmethod
    def difference(first: "TrackingInstances",
                   second: "TrackingInstances") -> "TrackingInstances":
        unique = TrackingInstances()
        for three_p, tokens_for_three_p in first.token_collection.items():
            if not second.has_third_party(three_p):
                unique.add_third_party_ids(three_p, tokens_for_three_p)
                continue

            for token, first_ps, in tokens_for_three_p.items():
                if second.has_token(three_p, token) is True:
                    continue
                unique.add_ids_for_token(three_p, token, first_ps)
        return unique

    @staticmethod
    def overlap(first: "TrackingInstances",
                second: "TrackingInstances") -> "TrackingInstances":
        overlap = TrackingInstances()
        for three_p, tokens_for_three_p in first.token_collection.items():
            if not second.has_third_party(three_p):
                continue
            for token, first_ps, in tokens_for_three_p.items():
                if not second.has_token(three_p, token):
                    continue
                overlap.add_ids_for_token(three_p, token, first_ps)
        return overlap

    def __init__(self) -> None:
        self.token_collection = {}

    def to_json(self, handle: Any) -> None:
        report: Dict[Any, Any] = {}
        for three_p, tokens_for_three_p in self.token_collection.items():
            for token, first_ps, in tokens_for_three_p.items():
                if len(first_ps) < 2:
                    continue
                if three_p not in report:
                    report[three_p] = {}
                loc, key, value = token
                report[three_p][f"{loc.name}::{key}::{value}"] = first_ps
        json.dump(report, handle)

    def to_pickle(self, handle: Any) -> None:
        pickle.dump(self, handle)

    def add_request(self, origin_1p: FirstPartyDomain,
                    origin_3p: ThirdPartyDomain, sent_tokens: List[Token],
                    ts: RequestTimestamp) -> None:
        if origin_3p not in self.token_collection:
            self.token_collection[origin_3p] = {}
        for token in sent_tokens:
            if token not in self.token_collection[origin_3p]:
                self.token_collection[origin_3p][token] = {}
            if origin_1p not in self.token_collection[origin_3p][token]:
                self.token_collection[origin_3p][token][origin_1p] = []
            self.token_collection[origin_3p][token][origin_1p].append(ts)

    def has_third_party(self, origin: ThirdPartyDomain) -> bool:
        try:
            self.token_collection[origin]
            return True
        except KeyError:
            return False

    def add_third_party_ids(self, origin: ThirdPartyDomain,
                            tokens: TokenIdentifications) -> None:
        if not self.has_third_party(origin):
            self.token_collection[origin] = tokens
        else:
            self.token_collection[origin] = {
                **self.token_collection[origin],
                **tokens}

    def has_token(self, origin: ThirdPartyDomain, token: Token) -> bool:
        try:
            self.token_collection[origin][token]
            return True
        except KeyError:
            return False

    def add_ids_for_token(self, origin: ThirdPartyDomain, token: Token,
                          identifications: FirstPartyIdentifications) -> None:
        if origin not in self.token_collection:
            self.token_collection[origin] = {}

        if token not in self.token_collection[origin]:
            self.token_collection[origin][token] = identifications
        else:
            self.token_collection[origin][token] = {
                **self.token_collection[origin][token],
                **identifications
            }

    def includes_token(self, origin: ThirdPartyDomain, token: Token) -> bool:
        if origin not in self.token_collection:
            return False
        if token not in self.token_collection[origin]:
            return False
        return True


class BrowserMeasurement:
    graph: MultiDiGraph
    debug: bool
    redirect_cache: RedirectCache

    def __init__(self, cache_path: Optional[pathlib.Path]) -> None:
        self.graph = MultiDiGraph()
        self.redirect_cache = RedirectCache(cache_path)
        self.debug = False

    def add_input_line(self, line: str) -> None:
        measurement = SiteMeasurement(json.loads(line), self.redirect_cache)
        measurement.debug = self.debug
        measurement.add_to_graph(self.graph)

    def add_input_file(self, file: Any) -> None:
        measurement = SiteMeasurement(json.load(file), self.redirect_cache)
        measurement.debug = self.debug
        measurement.add_to_graph(self.graph)

    def get_tracking_instances(self) -> TrackingInstances:
        track_instances = TrackingInstances()
        for u, v, data in self.graph.edges(data=True):
            # Ignore same party requests.
            if u == v:
                continue

            tokens = privacykpis.tokenizing.flaten_identifiers(data)
            # Ignore cases where there are no identifying tokens.
            if len(tokens) == 0:
                continue

            from_domain = cast(FirstPartyDomain, u)
            to_domain = cast(ThirdPartyDomain, v)
            node_data = cast(Dict[Any, Any], data)
            request_ts = cast(RequestTimestamp, (data[URL], data[TIMESTAMP]))
            track_instances.add_request(from_domain, to_domain, tokens,
                                        request_ts)
        return track_instances

    def close(self) -> None:
        self.redirect_cache.write()


def write(data: BrowserMeasurement, output_path: str) -> None:
    with open(output_path, "wb") as handle:
        pickle.dump(data, handle)


def graph_from_args(args: Args, debug: bool = False) -> BrowserMeasurement:
    measurement = BrowserMeasurement(args.redirect_cache_path)
    measurement.debug = debug
    for input_file in args.input:
        if args.multi:
            for line in input_file:
                if line.strip() == "":
                    continue
                measurement.add_input_line(line,)
        else:
            measurement.add_input_file(input_file)
    measurement.close()
    return measurement
