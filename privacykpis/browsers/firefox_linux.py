import os
import pathlib
import shutil
import subprocess
import time

from privacykpis.args import MeasureArgs, ConfigArgs
from privacykpis.consts import DEFAULT_FIREFOX_PROFILE
import privacykpis.environments.default


def launch_browser(args: MeasureArgs):
    # Sneak this in here because there are problems running Xvfb
    # as sudo, and sudo is needed for the *_env functions.
    from xvfbwrapper import Xvfb

    # Check to see if we need to copy the default firefox profile over to
    # wherever we're running from.
    if not pathlib.Path(args.profile_path).is_dir():
        shutil.copytree(str(DEFAULT_FIREFOX_PROFILE), args.profile_path)

    ff_args = [
        args.binary,
        "--profile", args.profile_path,
        args.url
    ]
    xvfb_handle = Xvfb()
    xvfb_handle.start()

    if args.debug:
        stdout_handle = None
        stderr_handle = None
    else:
        stdout_handle = subprocess.DEVNULL
        stderr_handle = subprocess.DEVNULL

    return [
        subprocess.Popen(ff_args, stdout=stdout_handle, stderr=stderr_handle),
        xvfb_handle
    ]

def close_browser(args: MeasureArgs, browser_info):
    if args.debug:
        subprocess.run([
            "import", "-window", "root", "-crop", "978x597+0+95", "-quality",
            "90", str(args.log_path) + ".json"
        ])
    browser_handle, xvfb_handle = browser_info
    browser_handle.terminate()
    xvfb_handle.stop()


setup_env = privacykpis.environments.default.setup_env
teardown_env = privacykpis.environments.default.teardown_env
