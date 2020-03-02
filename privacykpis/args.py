import os
import pathlib
import platform
import subprocess
import sys
from urllib.parse import urlparse

from privacykpis.consts import DEFAULT_FIREFOX_PROFILE
from privacykpis.consts import DEFAULT_PROXY_HOST, DEFAULT_PROXY_PORT
from privacykpis.consts import DEFAULT_LOCATIONS

def err(msg):
    print(msg, file=sys.stderr)


def has_certutil_installed():
    try:
        subprocess.run(["which", "certutil"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def validate_firefox(args):
    if not args.profile_path:
        err("no profile path provided")
        return False

    if pathlib.Path(args.profile_path) == DEFAULT_FIREFOX_PROFILE:
        err("don't write to the default firefox profile, "
            "point to either a different, existing profile, or a non-existing "
            "directory path, and a new profile will be created for you.")
        return False

    if not pathlib.Path(args.binary).is_file():
        err(args.binary + " is not a file")
        return False

    if args.proxy_host != DEFAULT_PROXY_HOST:
        err("cannot set custom proxy host on firefox")
        return False

    if args.proxy_port != DEFAULT_PROXY_PORT:
        err("cannot set custom proxy port on firefox")
        return False

    return True


def validate_chrome(args):
    if not args.profile_path:
        err("no profile path provided")
        return False

    if not pathlib.Path(args.binary).is_file():
        err(args.binary + " is not a file")
        return False
    return True


class Args:
    def valid(self):
        return self.is_valid


class ConfigArgs(Args):
    def __init__(self, args):
        self.is_valid = False

        if not args.install and not args.uninstall:
            err("Must select either 'install' or 'uninstall'")
            return

        if args.install and args.uninstall:
            err("Cannot select both 'install' or 'uninstall'")
            return

        is_root = os.geteuid() == 0
        if not is_root:
            err("you'll need to run as root to configure the environment")
            return

        self.uninstall = args.uninstall
        self.install = args.install
        self.case = args.case
        self.is_valid = True


class MeasureArgs(Args):
    def __init__(self, args):
        self.is_valid = False

        expected_url_parts = ["scheme", "netloc"]
        url_parts = urlparse(args.url)
        for index, part_name in enumerate(expected_url_parts):
            if url_parts[index] == "":
                err("invalid URL, missing a {}".format(part_name))
                return
        self.url = args.url

        if args.case == "safari":
            self.case = "safari"
            self.profile_path = None
            self.binary = "/Applications/Safari.app"
        elif args.case == "firefox":
            self.case = "firefox"
            if not args.binary:
                self.binary = DEFAULT_LOCATIONS["firefox"]
            else:
                self.binary = args.binary
            self.profile_path = args.profile_path
            self.proxy_host = args.proxy_host
            self.proxy_port = args.proxy_port
            if not validate_firefox(self):
                return
        else:  # chrome case
            self.case = args.case
            self.profile_path = args.profile_path
            if not args.binary:
                self.binary = DEFAULT_LOCATIONS["chrome"]
            else:
                self.binary = args.binary
            if not validate_chrome(self):
                return

        is_root = os.geteuid() == 0
        if is_root:
            err("please don't measure as root. Use sudo with ./environment.py "
                "and run this script as a less privilaged user")
            return

        self.case = args.case
        self.secs = args.secs
        self.proxy_host = args.proxy_host
        self.proxy_port = str(args.proxy_port)
        self.log = args.log
        self.debug = args.debug
        self.is_valid = True
