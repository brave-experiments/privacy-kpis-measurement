import subprocess

import privacykpis.common
import privacykpis.browsers
import privacykpis.environment
import privacykpis.environment.macos
import privacykpis.record
from privacykpis.types import RecordingHandles


class Browser(privacykpis.browsers.Interface):
    @staticmethod
    def launch(args: privacykpis.record.Args) -> RecordingHandles:
        less_privileged_user = privacykpis.common.get_real_user()
        command = ["open", args.url, "-g", "-a", args.binary]
        subprocess.run(command, check=True)
        return RecordingHandles()

    @staticmethod
    def close(args: privacykpis.record.Args,
              browser_handle: RecordingHandles) -> None:
        less_privileged_user = privacykpis.common.get_real_user()
        # a killed safari regenerates with previous session's tabs
        command = ["osascript", "-e", """quit app "Safari" """]
        subprocess.run(command, check=True)

    @staticmethod
    def setup_env(args: privacykpis.environment.Args) -> None:
        privacykpis.environment.macos.setup_env(args)

    @staticmethod
    def teardown_env(args: privacykpis.environment.Args) -> None:
        privacykpis.environment.macos.teardown_env(args)
