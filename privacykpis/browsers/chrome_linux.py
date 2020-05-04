from pathlib import Path
import subprocess
import typing

import privacykpis.browsers
import privacykpis.common
import privacykpis.consts
import privacykpis.environment
import privacykpis.record
from privacykpis.record import RecordingHandles


USER_CERT_DB_PATH = Path.home() / Path(".pki/nssdb")
USER_CERT_DB = "sql:{}".format(str(USER_CERT_DB_PATH))


class Browser(privacykpis.browsers.Interface):
    def launch(self, args: privacykpis.record.Args) -> RecordingHandles:
        # Sneak this in here because there are problems running Xvfb
        # as sudo, and sudo is needed for the *_env functions.
        from xvfbwrapper import Xvfb  # type: ignore

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

        browser_handle = subprocess.Popen(cr_args, stdout=stdout_handle,
                                          stderr=stderr_handle,
                                          universal_newlines=True)
        return RecordingHandles(browser=browser_handle, xvfb=xvfb_handle)

    def close(self, args: privacykpis.record.Args,
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

    def setup_env(self, args: privacykpis.environment.Args) -> None:
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

    def teardown_env(self, args: privacykpis.environment.Args) -> None:
        target_user = privacykpis.common.get_real_user()
        subprocess.run([
            "sudo", "-u", target_user, "certutil", "-D", "-d", USER_CERT_DB,
            "-n", "mitmproxy"])
