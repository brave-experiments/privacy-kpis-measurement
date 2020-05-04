import privacykpis.environment
import privacykpis.record
from privacykpis.record import RecordingHandles


class Interface:
    def launch(self, args: privacykpis.record.Args) -> RecordingHandles:
        return RecordingHandles()

    def close(self, args: privacykpis.record.Args,
              rec_handle: RecordingHandles) -> None:
        pass

    def setup_env(self, args: privacykpis.environment.Args) -> None:
        pass

    def teardown_env(self, args: privacykpis.environment.Args) -> None:
        pass
