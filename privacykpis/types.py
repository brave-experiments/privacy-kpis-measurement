from abc import abstractmethod, abstractproperty
import csv
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from xvfb import Xvfb  # type: ignore

SubProc = Any  # subprocess.Popen[AnyStr]


class TokenLocation(Enum):
    COOKIE = 1
    PATH = 2
    QUERY_PARAM = 3
    BODY = 4


RequestRec = Dict[Union["TokenLocation", str], Any]
Url = str
Domain = str
ThirdPartyDomain = Domain
FirstPartyDomain = Domain
ISOTimestamp = str
RequestTimestamp = Tuple[Url, ISOTimestamp]
TokenKey = str
TokenValue = str
KeyValueList = List[Tuple[TokenKey, TokenValue]]
Token = Tuple[TokenLocation, TokenKey, TokenValue]


class RecordingHandles:
    def __init__(self, browser: Optional[SubProc] = None,
                 xvfb: Optional["Xvfb"] = None) -> None:
        self.browser = browser
        self.xvfb = xvfb
