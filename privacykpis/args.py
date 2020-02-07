import os
import pathlib
import platform
import subprocess
import sys
from urllib.parse import urlparse

from privacykpis.consts import DEFAULT_FIREFOX_PROFILE
from privacykpis.consts import DEFAULT_PROXY_HOST, DEFAULT_PROXY_PORT


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
            if not validate_firefox(args):
                return
            self.case = "firefox"
            self.binary = args.binary
            self.profile_path = args.profile_path
        else:  # chrome case
            if not validate_chrome(args):
                return False
            self.case = args.case
            self.profile_path = args.profile_path
            self.binary = args.binary

        platform_name = platform.system()
        is_mac = platform_name == "Darwin"
        is_linux = platform_name == "Linux"
        is_root = os.geteuid() == 0

        # Try to avoid over privileging things where possible
        is_changing_certs = args.install is True or args.uninstall is True

        # If we're not mac AND changing certs, theres no need to run as root.
        if is_root and (not is_changing_certs or not is_mac):
            err("please don't run as root if you're not changing certs on mac")
            return

        if is_changing_certs:
            platform_name = platform.system()
            if is_mac and not is_root:
                err("must run as root if you want to modify certs on MacOS")
                return

            if is_linux and not has_certutil_installed():
                err("missing certutil (install something like libnss3-tools)")
                return

        self.case = args.case
        self.secs = args.secs
        self.proxy_host = args.proxy_host
        self.proxy_port = str(args.proxy_port)
        self.log = args.log

        self.uninstall = args.uninstall
        self.install = args.install
        self.is_valid = True

    def valid(self):
        return self.is_valid
