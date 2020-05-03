import pathlib
import shutil
import subprocess

import privacykpis.consts
import privacykpis.environment
import privacykpis.environment.default as default
import privacykpis.record


def launch_browser(args: privacykpis.record.Args):
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

    return subprocess.Popen(ff_args, stdout=stdout_handle,
                            stderr=stderr_handle)


def close_browser(args: privacykpis.record.Args, browser_handle):
    browser_handle.terminate()


setup_env = default.setup_env
teardown_env = default.teardown_env
