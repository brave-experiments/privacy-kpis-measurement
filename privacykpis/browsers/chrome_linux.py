import os
from pathlib import Path
import pathlib
import shutil
import subprocess
import tarfile
import time
import getpass

from privacykpis.args import MeasureArgs, ConfigArgs
from privacykpis.consts import RESOURCES_PATH
import privacykpis.common
from privacykpis.consts import LEAF_CERT


POLICIES_DIR_PATH = Path("/etc/opt/chrome/policies/recommended")
POLICIES_FILE_PATH = POLICIES_DIR_PATH / Path("recommended_policies.json")

USER_CERT_DB_PATH = Path.home() / Path(".pki/nssdb")
USER_CERT_DB = "sql:{}".format(str(USER_CERT_DB_PATH))


def launch_browser(args: MeasureArgs):
    # Sneak this in here because there are problems running Xvfb
    # as sudo, and sudo is needed for the *_env functions.
    from xvfbwrapper import Xvfb

    # Check to see if we need to copy the specialized profile over to
    # wherever we're storing the actively used profile.
    if hasattr(args,"profile_template") and not pathlib.Path(args.profile_path).is_dir():
        profile_template = RESOURCES_PATH / args.profile_template
        subprocess.run(["mkdir","-p",str(args.profile_path)])
        with tarfile.open(profile_template) as tf:
            tf.extractall(args.profile_path)

    if os.path.islink(os.path.join(args.profile_path,"SingletonLock")):
        os.unlink(os.path.join(args.profile_path,"SingletonLock"))

    cr_args = [
        args.binary,
        "--user-data-dir=" + args.profile_path,
        "--proxy-server={}:{}".format(args.proxy_host, args.proxy_port),
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
        subprocess.Popen(cr_args, stdout=stdout_handle, stderr=stderr_handle),
        xvfb_handle
    ]


def close_browser(args: MeasureArgs, browser_info):
    browser_handle, xvfb_handle = browser_info
    browser_handle.terminate()
    xvfb_handle.stop()


def setup_env(args: ConfigArgs):
    target_user = privacykpis.common.get_real_user()
    setup_args = [
        # Create the nssdb directory for this user.
        ["mkdir", "-p", str(USER_CERT_DB_PATH)],
        # Create an empty CA container / database.
        ["certutil", "-N", "-d", USER_CERT_DB, "--empty-password"],
        # Add the mitmproxy cert to the newly created database.
        ["certutil", "-A", "-d", USER_CERT_DB, "-i", str(LEAF_CERT), "-n",
            "mitmproxy", "-t", "TC,TC,TC"]
    ]
    sudo_prefix = ["sudo", "-u", target_user]
    for args in setup_args:
        subprocess.run(sudo_prefix + args)


def teardown_env(args: ConfigArgs):
    target_user = privacykpis.common.get_real_user()
    subprocess.run([
        "sudo", "-u", target_user, "certutil", "-D", "-d", USER_CERT_DB, "-n",
        "mitmproxy"])
