import pathlib
import shutil
import subprocess

import privacykpis.consts
import privacykpis.browsers
import privacykpis.environment
import privacykpis.record
from privacykpis.record import RecordingHandles


class Browser(privacykpis.browsers.Interface):
    @staticmethod
    def launch(args: privacykpis.record.Args) -> RecordingHandles:
        # Check to see if we need to copy the default firefox profile over to
        # wherever we're running from.
        if not pathlib.Path(args.profile_path).is_dir():
            shutil.copytree(str(privacykpis.consts.DEFAULT_FIREFOX_PROFILE),
                            args.profile_path)

        ff_args = [
            args.binary,
            "--profile", args.profile_path,
            args.url
        ]

        if args.debug:
            stdout_handle = None
            stderr_handle = None
        else:
            stdout_handle = subprocess.DEVNULL
            stderr_handle = subprocess.DEVNULL

        browser_handle = subprocess.Popen(ff_args, stdout=stdout_handle,
                                          stderr=stderr_handle,
                                          universal_newlines=True)
        return RecordingHandles(browser=browser_handle)

    @staticmethod
    def close(args: privacykpis.record.Args,
              rec_handle: RecordingHandles) -> None:
        if rec_handle.browser:
            rec_handle.browser.terminate()
