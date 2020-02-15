import os
import subprocess
import time

from privacykpis.args import MeasureArgs
import privacykpis.environments.macos


def launch_browser(args: MeasureArgs):
    less_privileged_user = os.getlogin()
    args = [
        "open", args.url, "-g", "-a", args.binary]
    subprocess.run(args, check=True)
    return None


def close_browser(args: MeasureArgs, browser_handle):
    less_privileged_user = os.getlogin()
    args = ["killall", "-u", less_privileged_user, "Safari"]
    subprocess.run(args, check=True)


setup_env = privacykpis.environments.macos.setup_env
teardown_env = privacykpis.environments.macos.teardown_env
