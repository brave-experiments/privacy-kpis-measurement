import os
from pathlib import Path
import subprocess

from privacykpis.args import Args
from privacykpis.consts import LEAF_CERT


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
