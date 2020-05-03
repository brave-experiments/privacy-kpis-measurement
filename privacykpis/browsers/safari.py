import subprocess

import privacykpis.common
import privacykpis.environments.macos
import privacykpis.record


def launch_browser(args: privacykpis.record.Args):
    less_privileged_user = privacykpis.common.get_real_user()
    args = ["open", args.url, "-g", "-a", args.binary]
    subprocess.run(args, check=True)
    return None


def close_browser(args: privacykpis.record.Args, browser_handle):
    less_privileged_user = privacykpis.common.get_real_user()
    args = ["killall", "-u", less_privileged_user, "Safari"]
    subprocess.run(args, check=True)


setup_env = privacykpis.environments.macos.setup_env
teardown_env = privacykpis.environments.macos.teardown_env
