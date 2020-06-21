import argparse
import json
import pathlib
import subprocess
import time
from typing import Any, AnyStr, Tuple, Optional, Type, TYPE_CHECKING, Union
import urllib.parse

from xvfbwrapper import Xvfb  # type: ignore

import privacykpis.args
import privacykpis.browsers
import privacykpis.common
from privacykpis.common import err
from privacykpis.consts import CERT_PATH, LOG_HEADERS_SCRIPT_PATH
from privacykpis.consts import DEFAULT_FIREFOX_PROFILE, DEFAULT_PROXY_HOST
from privacykpis.consts import DEFAULT_PROXY_PORT
from privacykpis.types import SubProc


def validate_firefox(args: argparse.Namespace) -> bool:
    if not args.profile_path:
        err("no profile path provided")
        return False

    if pathlib.Path(args.profile_path) == DEFAULT_FIREFOX_PROFILE:
        err("don't write to the default firefox profile, "
            "point to either a different, existing profile, or a non-existing "
            "directory path, and a new profile will be created for you.")
        return False

    if not pathlib.Path(args.binary).is_file():
        err(f"{args.binary} is not a file")
        return False

    if args.proxy_host != DEFAULT_PROXY_HOST:
        err("cannot set custom proxy host on firefox")
        return False

    if args.proxy_port != DEFAULT_PROXY_PORT:
        err("cannot set custom proxy port on firefox")
        return False

    return True


def validate_chrome(args: argparse.Namespace) -> bool:
    if not args.profile_path:
        err("no profile path provided")
        return False

    if not pathlib.Path(args.binary).is_file():
        err(f"{args.binary} is not a file")
        return False
    return True


class Args(privacykpis.args.Args):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

        if args.url:
            expected_url_parts = ["scheme", "netloc"]
            url_parts = urllib.parse.urlparse(args.url)
            for index, part_name in enumerate(expected_url_parts):
                if url_parts[index] == "":
                    err(f"invalid URL, missing a {part_name}")
                    return
            self.url = args.url
        else:
            if not args.profile_index or not args.queue_host:
                err("to measure urls from a queue, you must "
                "provide a redis host and a profile index.")
                return
            self.profile_index = args.profile_index
            self.queue_host = args.queue_host
            self.output_queue = args.output_queue
            self.url = None

        if args.case == "safari":
            self.case = "safari"
            self.profile_path = ""
            self.binary = "/Applications/Safari.app"
        elif args.case == "firefox":
            if not validate_firefox(args):
                return
            self.case = "firefox"
            self.binary = args.binary
            self.profile_path = args.profile_path
        else:  # chrome case
            if not validate_chrome(args):
                return
            self.case = args.case
            self.profile_path = args.profile_path
            self.binary = args.binary

        if privacykpis.common.is_root():
            err("please don't measure as root. "
                "Use sudo with ./environment.py and run "
                "this script as a less privilaged user")
            return

        self.case = args.case
        self.secs = args.secs
        self.proxy_host = args.proxy_host
        self.proxy_port = str(args.proxy_port)
        self.log = args.log
        self.is_valid = True


def setup_proxy_for_url(args: Args) -> Optional[SubProc]:
    mitmdump_args = [
        "mitmdump",
        "--listen-host", args.proxy_host,
        "--listen-port", args.proxy_port,
        "-s", str(LOG_HEADERS_SCRIPT_PATH),
        "--set", f"confdir={CERT_PATH}",
        "-q",
        json.dumps(dict(privacy_kpis_url=args.url, privacy_kpis_log=args.log))
    ]

    proxy_handle = subprocess.Popen(mitmdump_args, stderr=None,
                                    universal_newlines=True)
    if args.debug:
        print("Waiting 5 sec for mitmproxy to spin up...")
    time.sleep(5)
    if proxy_handle.poll() is not None:
        print("Something went sideways when running mitmproxy:")
        print("\t" + " ".join(mitmdump_args))
        return None

    return proxy_handle


def teardown_proxy(proxy_handle: SubProc, args: Args) -> None:
    if args.debug:
        print("Shutting down, giving proxy time to write log")
    proxy_handle.terminate()
    proxy_handle.wait()


def run(args: Args) -> None:
    browser = privacykpis.browsers.browser_class(args)
    proxy_handle = setup_proxy_for_url(args)
    if proxy_handle is None:
        return

    browser_info = browser.launch(args)
    if args.debug:
        print("browser loaded, waiting {} secs".format(args.secs))
    time.sleep(args.secs)
    if args.debug:
        print("measurement complete, tearing down")
    browser.close(args, browser_info)

    teardown_proxy(proxy_handle, args)
