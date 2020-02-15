import os
import subprocess
import time

from privacykpis.args import MeasureArgs
import privacykpis.environments.macos


def launch_browser(args: MeasureArgs):
    args = [
        args.binary,
        "--user-data-dir=" + args.profile_path,
        args.url
    ]
    return subprocess.Popen(args)


def close_browser(args: MeasureArgs, browser_handle):
    browser_handle.terminate()


setup_env = privacykpis.environments.macos.setup_env
teardown_env = privacykpis.environments.macos.teardown_env
