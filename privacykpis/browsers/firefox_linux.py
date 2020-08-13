import pathlib
import shutil
import subprocess

import privacykpis.browsers
import privacykpis.common
import privacykpis.consts
import privacykpis.record
from privacykpis.types import RecordingHandles


class Browser(privacykpis.browsers.Interface):
    @staticmethod
    def launch(args: privacykpis.record.Args, url: str) -> RecordingHandles:
        # Sneak this in here because there are problems running Xvfb
        # as sudo, and sudo is needed for the *_env functions.
        from xvfbwrapper import Xvfb  # type: ignore

        # Check to see if we need to copy the default firefox profile over to
        # wherever we're running from.
        if not pathlib.Path(args.profile_path).is_dir():
            shutil.copytree(str(privacykpis.consts.DEFAULT_FIREFOX_PROFILE),
                            args.profile_path)

        ff_args = [
            args.binary,
            "--profile", args.profile_path,
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

        browser_handle = subprocess.Popen(ff_args, stdout=stdout_handle,
                                          stderr=stderr_handle,
                                          universal_newlines=True)
        return RecordingHandles(browser=browser_handle, xvfb=xvfb_handle)

    @staticmethod
    def close(args: privacykpis.record.Args,
              rec_handles: RecordingHandles) -> None:
        if args.debug:
            subprocess.run([
                "import", "-window", "root", "-crop", "978x597+0+95",
                "-quality", "90", str(args.log) + ".png"
            ])
        if rec_handles.browser:
            rec_handles.browser.terminate()
        if rec_handles.xvfb:
            rec_handles.xvfb.stop()
        Browser.sweep()
