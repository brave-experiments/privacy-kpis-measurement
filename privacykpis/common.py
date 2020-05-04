import json
import os
import pathlib
import platform
import sys
import types
from typing import Union

import privacykpis.browsers
import privacykpis.environment
import privacykpis.record


SubProcessArgs = Union[
    privacykpis.environment.Args,
    privacykpis.record.Args
]


def err(msg: str) -> None:
    print(msg, file=sys.stderr)


def get_real_user() -> str:
    return pathlib.Path.home().owner()


def is_root() -> bool:
    return os.geteuid() == 0


def browser_for_args(args: SubProcessArgs) -> privacykpis.browsers.Interface:
    platform_name = platform.system()
    is_linux = platform_name == "Linux"
    is_mac = platform_name == "Darwin"

    browser_interface: privacykpis.browsers.Interface
    if args.case == "safari":
        if is_mac:
            import privacykpis.browsers.safari as safari_module
            browser_interface = safari_module.Browser()
    elif args.case == "chrome":
        if is_linux:
            import privacykpis.browsers.chrome_linux as chrome_linux_module
            browser_interface = chrome_linux_module.Browser()
    elif args.case == "firefox":
        if is_mac:
            import privacykpis.browsers.firefox_macos as firefox_macos_module
            browser_interface = firefox_macos_module.Browser()
        elif is_linux:
            import privacykpis.browsers.firefox_linux as firefox_linux_module
            browser_interface = firefox_linux_module.Browser()

    if browser_interface is None:
        msg = "{} on {} is not currently implemented".format(
            args.case, platform_name)
        raise RuntimeError(msg)

    return browser_interface
