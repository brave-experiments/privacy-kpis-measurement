import os
import pathlib
import shutil
import subprocess
import time

from privacykpis.args import Args
from privacykpis.consts import DEFAULT_FIREFOX_PROFILE
import privacykpis.environments.linux


def launch_browser(args: Args):
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


def close_browser(args: Args, browser_handle):
    browser_handle.terminate()


setup_env = privacykpis.environments.linux.setup_env
teardown_env = privacykpis.environments.linux.teardown_env
