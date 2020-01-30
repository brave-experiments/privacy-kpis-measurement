import os
import subprocess

from xvfbwrapper import Xvfb

from privacykpis.args import Args
import privacykpis.environments.linux


def launch_browser(args: Args):
  less_privileged_user = os.getlogin()
  args = [
    "sudo", "-u", less_privileged_user,
    args.binary,
    "--user-data-dir=" + args.profile_path,
    "--proxy-server='{}:{}'".format(args.proxy_host, args.proxy_port),
    args.url
  ]
  xvfb_handle = Xvfb()
  xvfb_handle.start()
  return [subprocess.Popen(args), xvfb_handle]


def close_browser(args: Args, browser_info):
  browser_handle, xvfb_handle = browser_info
  xvfb_handle.stop()
  browser_handle.terminate()


setup_env = privacykpis.environments.linux.setup_env
teardown_env = privacykpis.environments.linux.teardown_env