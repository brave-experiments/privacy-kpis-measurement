import json
from pathlib import Path
import subprocess
from typing import Any, Dict, List, Union

import privacykpis.browsers
import privacykpis.common
import privacykpis.consts
import privacykpis.environment
import privacykpis.record
from privacykpis.types import RecordingHandles


USER_CERT_DB_PATH = Path.home() / Path(".pki/nssdb")
USER_CERT_DB = "sql:{}".format(str(USER_CERT_DB_PATH))
CHROMIUM_POLICIES_DIR = Path("/etc/chromium/policies")
CHROME_POLICIES_DIR = Path("/etc/opt/chrome/policies")
POLICY_FILE_NAME = Path("chrome_policy.json")


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


class Browser(privacykpis.browsers.Interface):
    @staticmethod
    def launch(args: privacykpis.record.Args, url: str) -> RecordingHandles:
        # Sneak this in here because there are problems running Xvfb
        # as sudo, and sudo is needed for the *_env functions.
        from xvfbwrapper import Xvfb  # type: ignore

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
        if rec_handle.xvfb:
            rec_handle.xvfb.stop()

    @staticmethod
    def setup_env(args: privacykpis.environment.Args) -> None:
        target_user = privacykpis.common.get_real_user()
        setup_args = [
            # Create the nssdb directory for this user.
            ["mkdir", "-p", str(USER_CERT_DB_PATH)],
            # Create an empty CA container / database.
            ["certutil", "-N", "-d", USER_CERT_DB, "--empty-password"],
            # Add the mitmproxy cert to the newly created database.
            ["certutil", "-A", "-d", USER_CERT_DB, "-i",
                str(privacykpis.consts.LEAF_CERT), "-n", "mitmproxy", "-t",
                "TC,TC,TC"]
        ]
        sudo_prefix = ["sudo", "-u", target_user]
        for command in setup_args:
            subprocess.run(sudo_prefix + command)
        _setup_managed_policies()

    @staticmethod
    def teardown_env(args: privacykpis.environment.Args) -> None:
        target_user = privacykpis.common.get_real_user()
        subprocess.run([
            "sudo", "-u", target_user, "certutil", "-D", "-d", USER_CERT_DB,
            "-n", "mitmproxy"])
        _remove_managed_policies()
