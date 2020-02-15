import os
import pathlib
import shutil
import subprocess
import time

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
    return subprocess.Popen(args)


def close_browser(args: MeasureArgs, browser_handle):
    browser_handle.terminate()


setup_env = privacykpis.environments.default.setup_env
teardown_env = privacykpis.environments.default.teardown_env
