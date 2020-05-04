import subprocess

import privacykpis.common
import privacykpis.browsers
import privacykpis.environment.macos
import privacykpis.record
from privacykpis.record import RecordingHandles


class Browser(privacykpis.browsers.Interface):
    def launch(self, args: privacykpis.record.Args) -> RecordingHandles:
        less_privileged_user = privacykpis.common.get_real_user()
        command = ["open", args.url, "-g", "-a", args.binary]
        subprocess.run(command, check=True)
        return RecordingHandles()

    def close(self, args: privacykpis.record.Args,
              browser_handle: RecordingHandles) -> None:
        less_privileged_user = privacykpis.common.get_real_user()
        command = ["killall", "-u", less_privileged_user, "Safari"]
        subprocess.run(command, check=True)
