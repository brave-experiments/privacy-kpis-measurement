from abc import abstractmethod, abstractproperty
import csv
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from xvfb import Xvfb  # type: ignore
    from privacykpis.tokenizing import TokenLocation

SubProc = Any  # subprocess.Popen[AnyStr]


class CSVWriter:
    @abstractmethod
    def writerow(self, row: List[str]) -> None:
        pass

    @abstractmethod
    def writerows(self, rows: List[List[str]]) -> None:
        pass

    @abstractproperty
    def dialect(self) -> csv.Dialect:
        pass


RequestRec = Dict[Union["TokenLocation", str], Any]


class RecordingHandles:
    def __init__(self, browser: Optional[SubProc] = None,
                 xvfb: Optional["Xvfb"] = None) -> None:
        self.browser = browser
        self.xvfb = xvfb
