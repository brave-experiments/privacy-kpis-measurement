import os
from pathlib import Path
import subprocess
import time

from xvfbwrapper import Xvfb

from privacykpis.args import Args
from privacykpis.consts import LEAF_CERT
import privacykpis.environments.linux


CHROME_CERT_PATH = Path.home() / Path(".pki/nssdb")
CHROME_CERT_URI = "sql:" + str(CHROME_CERT_PATH)


def launch_browser(args: Args):
    args = [
        args.binary,
        "--user-data-dir=" + args.profile_path,
        "--proxy-server='{}:{}'".format(args.proxy_host, args.proxy_port),
        args.url
    ]
    xvfb_handle = Xvfb()
    xvfb_handle.start()
    return [subprocess.Popen(args), xvfb_handle]


def close_browser(args: Args, browser_info):
    browser_handle, xvfb_handle = browser_info
    browser_handle.terminate()
    xvfb_handle.stop()


def setup_env(args: Args):
    if not CHROME_CERT_PATH.is_dir():
        CHROME_CERT_PATH.mkdir()
    install_cert_args = [
        "certutil", "-A",
        "-n", "mitmproxy",
        "-d", CHROME_CERT_URI,
        "-t", "C,,",
        "-i", str(LEAF_CERT)
    ]
    subprocess.run(install_cert_args, check=True)


def teardown_env(args: Args):
    uninstall_cert_args = [
        "certutil", "-D",
        "-d", CHROME_CERT_URI,
        "-n", "mitmproxy"
    ]
    subprocess.run(uninstall_cert_args, check=True)
