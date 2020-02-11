import os
from pathlib import Path
import subprocess
import time

from xvfbwrapper import Xvfb

from privacykpis.args import Args
import privacykpis.environments.linux


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
    user_home_dir = str(Path.home())
    install_cert_args = [
        "certutil", "-A",
        "-n", "mitmproxy",
        "-d", "sql:{}/.pki/nssdb".format(user_home_dir),
        "-t", "C,,",
        "-i", str(LEAF_CERT)
    ]
    subprocess.run(install_cert_args, check=True)


def teardown_env(args: Args):
    user_home_dir = str(Path.home())
    uninstall_cert_args = [
        "certutil", "-D",
        "-d", "sql:{}/.pki/nssdb".format(user_home_dir),
        "-n", "mitmproxy"
    ]
    subprocess.run(uninstall_cert_args, check=True)
