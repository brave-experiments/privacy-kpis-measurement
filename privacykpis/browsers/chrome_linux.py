import os
from pathlib import Path
import subprocess
import time

from xvfbwrapper import Xvfb

from privacykpis.args import MeasureArgs, ConfigArgs
from privacykpis.consts import LEAF_CERT, CHROMIUM_POLICY_PATH


POLICIES_DIR_PATH = Path("/etc/opt/chrome/policies/recommended")
POLICIES_FILE_PATH = POLICIES_DIR_PATH / Path("recommended_policies.json")


def launch_browser(args: MeasureArgs):
    args = [
        args.binary,
        "--user-data-dir=" + args.profile_path,
        "--proxy-server='{}:{}'".format(args.proxy_host, args.proxy_port),
        args.url
    ]
    xvfb_handle = Xvfb()
    xvfb_handle.start()
    return [subprocess.Popen(args), xvfb_handle]


def close_browser(args: MeasureArgs, browser_info):
    browser_handle, xvfb_handle = browser_info
    browser_handle.terminate()
    xvfb_handle.stop()


def setup_env(args: ConfigArgs):
    if not POLICIES_DIR_PATH.is_dir():
        POLICIES_DIR_PATH.mkdir(parents=True, exist_ok=True)

    if not POLICIES_FILE_PATH.is_file():
        POLICIES_FILE_PATH.write_text(CHROMIUM_POLICY_PATH.read_text())


def teardown_env(args: ConfigArgs):
    # Only remove the environment's chrome policy file if it 100% matches
    # the one we installed in the first place.
    if not POLICIES_FILE_PATH.is_file():
        return

    our_policy_text = CHROMIUM_POLICY_PATH.read_text()
    current_policy_text = POLICIES_FILE_PATH.read_text()
    if our_policy_text != current_policy_text:
        return

    POLICIES_FILE_PATH.unlink()
