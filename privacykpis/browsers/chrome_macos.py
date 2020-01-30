import os
import subprocess
import time

from privacykpis.args import Args
import privacykpis.environments.macos


def launch_browser(args: Args):
  less_privileged_user = os.getlogin()
  args = [
    "sudo", "-u", less_privileged_user,
    args.binary,
    "--user-data-dir=" + args.profile_path,
    args.url
  ]
  return subprocess.Popen(args)


def close_browser(args: Args, browser_handle):
  browser_handle.terminate()


setup_env = privacykpis.environments.macos.setup_env
teardown_env = privacykpis.environments.macos.teardown_env