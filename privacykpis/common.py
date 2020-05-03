import json
import os
import pathlib
import platform

from privacykpis.args import Args


def err(msg):
    print(msg, file=sys.stderr)


def get_real_user():
    return pathlib.Path.home().owner()


def is_root():
    return os.geteuid() == 0


def module_for_args(args: Args):
    platform_name = platform.system()
    is_linux = platform_name == "Linux"
    is_mac = platform_name == "Darwin"

    case_module = None
    if args.case == "safari":
        if is_mac:
            import privacykpis.browsers.safari as safari_module
            case_module = safari_module
    elif args.case == "chrome":
        if is_linux:
            import privacykpis.browsers.chrome_linux as chrome_linux_module
            case_module = chrome_linux_module
    elif args.case == "firefox":
        if is_mac:
            import privacykpis.browsers.firefox_macos as firefox_macos_module
            case_module = firefox_macos_module
        elif is_linux:
            import privacykpis.browsers.firefox_linux as firefox_linux_module
            case_module = firefox_linux_module

    if case_module is None:
        msg = "{} on {} is not currently implemented".format(
            args.case, platform_name)
        raise RuntimeError(msg)

    return case_module
