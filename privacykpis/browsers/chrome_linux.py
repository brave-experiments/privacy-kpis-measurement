import getpass
import json
import os
from pathlib import Path
import pathlib
import shutil
import subprocess
import tarfile
import time
from typing import Any, Dict, List, Union

from privacykpis.consts import CHROME_LEAF_CERT, RESOURCES_PATH
import privacykpis.common
import privacykpis.consts
import privacykpis.environment
import privacykpis.record
from privacykpis.types import RecordingHandles


CHROMIUM_POLICIES_DIR = Path("/etc/chromium/policies")
CHROME_POLICIES_DIR = Path("/etc/opt/chrome/policies")
POLICY_FILE_NAME = Path("chrome_policy.json")


def _user_cert_db_path(args: privacykpis.environment.Args) -> Path:
    return Path(f"/home/{args.crawl_user}/.pki/nssdb")


def _user_cert_db(args: privacykpis.environment.Args) -> str:
    return f"sql:{_user_cert_db_path(args)}"


def _setup_managed_policies() -> None:
    for policy_root in (CHROMIUM_POLICIES_DIR, CHROME_POLICIES_DIR):
        managed_policy_dir = policy_root / Path("managed")
        managed_policy_dir.mkdir(parents=True, exist_ok=True)
        managed_policy_file = managed_policy_dir / POLICY_FILE_NAME
        policy_text = privacykpis.consts.CHROME_POLICY_PATH.read_text()
        managed_policy_file.write_text(policy_text)


def _remove_managed_policies() -> None:
    for policy_root in (CHROMIUM_POLICIES_DIR, CHROME_POLICIES_DIR):
        managed_policy_dir = policy_root / Path("managed")
        managed_policy_file = managed_policy_dir / POLICY_FILE_NAME
        if managed_policy_dir.is_dir():
            if managed_policy_file.is_file():
                managed_policy_file.unlink()
            managed_policy_dir.rmdir()


def _write_json_key(data: Dict[str, Any], key_path: List[str],
                    value: Union[str, bool, int]) -> bool:
    try:
        current_data = data
        index_keys = key_path[:-1]
        last_key = key_path[-1]
        for key in index_keys:
            current_data = current_data[key]
        current_data[last_key] = value
        return True
    except KeyError:
        return False


def _edit_profile_to_prevent_session_restore(profile_path: str) -> None:
    profile_dir = Path(profile_path)

    def_prefs_path = profile_dir / Path("Default/Preferences")
    if def_prefs_path.is_file():
        read_handle = def_prefs_path.open("r")
        data = json.load(read_handle)
        read_handle.close()

        _write_json_key(data, ["profile", "exited_cleanly"], True)
        _write_json_key(data, ["profile", "exit_type"], "Normal")

        write_handle = def_prefs_path.open("w")
        json.dump(data, write_handle)
        write_handle.close()

    # Only used in Brave, to the best of my knowledge (@pes)
    local_state_path = profile_dir / Path("Local State")
    if local_state_path.is_file():
        read_handle = def_prefs_path.open("r")
        data = json.load(read_handle)
        read_handle.close()

        exited_cleanly_path = ["user_experience_metrics", "stability",
                               "exited_cleanly"]
        _write_json_key(data, exited_cleanly_path, True)

        write_handle = def_prefs_path.open("w")
        json.dump(data, write_handle)
        write_handle.close()

    singleton_path = profile_dir / Path("SingletonLock")
    if singleton_path.is_symlink():
        singleton_path.unlink()


class Browser(privacykpis.browsers.Interface):
    @staticmethod
    def launch(args: privacykpis.record.Args, url: str) -> RecordingHandles:
        # Sneak this in here because there are problems running Xvfb
        # as sudo, and sudo is needed for the *_env functions.
        from xvfbwrapper import Xvfb  # type: ignore

        # Check to see if we need to copy the specialized profile over to
        # wherever we're storing the actively used profile.
        if args.profile_template is not None:
            possible_profile_path = Path(args.profile_path)
            if not possible_profile_path.is_dir():
                profile_template = RESOURCES_PATH / args.profile_template
                possible_profile_path.mkdir(parents=True)
                with tarfile.open(profile_template) as tf:
                    tf.extractall(args.profile_path)

        _edit_profile_to_prevent_session_restore(args.profile_path)

        cr_args = [
            args.binary,
            "--user-data-dir=" + args.profile_path,
            "--proxy-server={}:{}".format(args.proxy_host, args.proxy_port),
            url
        ]
        xvfb_handle = Xvfb()
        xvfb_handle.start()

        if args.debug:
            stdout_handle = None
            stderr_handle = None
        else:
            stdout_handle = subprocess.DEVNULL
            stderr_handle = subprocess.DEVNULL

        browser_handle = subprocess.Popen(cr_args, stdout=stdout_handle,
                                          stderr=stderr_handle,
                                          universal_newlines=True)
        return RecordingHandles(browser=browser_handle, xvfb=xvfb_handle)

    @staticmethod
    def close(args: privacykpis.record.Args,
              rec_handle: RecordingHandles) -> None:
        if args.debug:
            subprocess.run([
                "import", "-window", "root", "-crop", "978x597+0+95",
                "-quality", "90", str(args.log) + ".png"
            ])
        if rec_handle.browser:
            rec_handle.browser.terminate()
            rec_handle.browser.wait()
        if rec_handle.xvfb:
            rec_handle.xvfb.stop()
        Browser.sweep()

    @staticmethod
    def setup_env(args: privacykpis.environment.Args) -> None:
        target_user = args.crawl_user
        user_cert_db_path = _user_cert_db_path(args)
        user_cert_db = _user_cert_db(args)

        setup_args = [
            # Create the nssdb directory for this user.
            ["mkdir", "-p", str(user_cert_db_path)],
            # Create an empty CA container / database.
            ["certutil", "-N", "-d", user_cert_db, "--empty-password"],
            # Add the mitmproxy cert to the newly created database.
            ["certutil", "-A", "-d", user_cert_db, "-i",
                str(CHROME_LEAF_CERT), "-n", "mitmproxy", "-t",
                "C,,"]
        ]
        sudo_prefix = ["sudo", "-u", target_user]
        for command in setup_args:
            cmd = sudo_prefix + command
            if args.debug:
                print("setup_env: " + " ".join(cmd))
            subprocess.run(cmd)
        _setup_managed_policies()

    @staticmethod
    def teardown_env(args: privacykpis.environment.Args) -> None:
        user_cert_db_path = _user_cert_db_path(args)
        if user_cert_db_path.is_dir():
            subprocess.run(["sudo", "rm", "-Rf", str(user_cert_db_path)])
        _remove_managed_policies()
