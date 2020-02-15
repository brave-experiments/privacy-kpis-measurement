import os
import pathlib
import shutil
import subprocess
import time

from xvfbwrapper import Xvfb

from privacykpis.args import MeasureArgs, ConfigArgs
from privacykpis.consts import DEFAULT_FIREFOX_PROFILE
import privacykpis.environments.default


def launch_browser(args: MeasureArgs):
    # Check to see if we need to copy the default firefox profile over to
    # wherever we're running from.
    if not pathlib.Path(args.profile_path).is_dir():
        shutil.copytree(str(DEFAULT_FIREFOX_PROFILE), args.profile_path)

    args = [
        args.binary,
        "--profile", args.profile_path,
        args.url
    ]
    xvfb_handle = Xvfb()
    xvfb_handle.start()
    return [subprocess.Popen(args), xvfb_handle]


def close_browser(args: MeasureArgs, browser_info):
    browser_handle, xvfb_handle = browser_info
    browser_handle.terminate()
    xvfb_handle.stop()


setup_env = privacykpis.environments.default.setup_env
teardown_env = privacykpis.environments.default.teardown_env
