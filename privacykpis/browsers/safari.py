import os
import subprocess
import time

from privacykpis.args import Args
import privacykpis.environments.macos


def launch_browser(args: Args):
    less_privileged_user = os.getlogin()
    args = [
        # noop when not running as root / sudo.
        "sudo", "-u", less_privileged_user,
        "open", args.url, "-g", "-a", args.binary]
    subprocess.run(args, check=True)
    return None


def close_browser(args: Args, browser_handle):
    less_privileged_user = os.getlogin()
    args = ["killall", "-u", less_privileged_user, "Safari"]
    subprocess.run(args, check=True)


setup_env = privacykpis.environments.macos.setup_env
teardown_env = privacykpis.environments.macos.teardown_env
