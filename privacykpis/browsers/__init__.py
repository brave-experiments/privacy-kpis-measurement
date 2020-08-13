import platform
import os
import errno
import sys
from typing import Optional, Type, TYPE_CHECKING, Union

from privacykpis.types import RecordingHandles

if TYPE_CHECKING:
    import privacykpis.environment
    import privacykpis.record

SubProcessArgs = Union[
    "privacykpis.environment.Args",
    "privacykpis.record.Args"
]

BrowserInterface = Type["Interface"]


class Interface:
    @staticmethod
    def launch(args: "privacykpis.record.Args", url: str) -> RecordingHandles:
        return RecordingHandles()

    @staticmethod
    def close(args: "privacykpis.record.Args",
              rec_handle: RecordingHandles) -> None:
        pass

    @staticmethod
    def setup_env(args: "privacykpis.environment.Args") -> None:
        pass

    @staticmethod
    def teardown_env(args: "privacykpis.environment.Args") -> None:
        pass

    @staticmethod
    def sweep() -> None:
        try:
            while os.waitpid(-1, os.WNOHANG) != (0, 0):
                pass
        except OSError as e:
            if e.errno != errno.ECHILD:
                print(f"unexpected error: {e}")
            else:
                print(f"waited a zombie: {e}")


def browser_class(args: SubProcessArgs) -> BrowserInterface:
    platform_name = platform.system()
    is_linux = platform_name == "Linux"
    is_mac = platform_name == "Darwin"

    browser_interface: Optional[BrowserInterface] = None
    if args.case == "safari":
        if is_mac:
            import privacykpis.browsers.safari as safari_module
            browser_interface = safari_module.Browser
    elif args.case == "chrome":
        if is_linux:
            import privacykpis.browsers.chrome_linux as chrome_linux_module
            browser_interface = chrome_linux_module.Browser
    elif args.case == "firefox":
        if is_mac:
            import privacykpis.browsers.firefox_macos as firefox_macos_module
            browser_interface = firefox_macos_module.Browser
        elif is_linux:
            import privacykpis.browsers.firefox_linux as firefox_linux_module
            browser_interface = firefox_linux_module.Browser

    if browser_interface is None:
        msg = "{} on {} is not currently implemented".format(
            args.case, platform_name)
        raise RuntimeError(msg)

    return browser_interface
