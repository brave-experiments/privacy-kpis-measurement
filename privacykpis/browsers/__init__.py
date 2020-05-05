import privacykpis.environment
import privacykpis.record
from privacykpis.record import RecordingHandles


class Interface:
    @staticmethod
    def launch(args: privacykpis.record.Args) -> RecordingHandles:
        return RecordingHandles()

    @staticmethod
    def close(args: privacykpis.record.Args,
              rec_handle: RecordingHandles) -> None:
        pass

    @staticmethod
    def setup_env(args: privacykpis.environment.Args) -> None:
        pass

    @staticmethod
    def teardown_env(args: privacykpis.environment.Args) -> None:
        pass
