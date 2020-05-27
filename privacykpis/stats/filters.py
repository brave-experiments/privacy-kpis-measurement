import mimetypes
import time
from typing import Any, Callable, Dict, List, Optional
import dateutil.parser

from privacykpis.stats.utilities import ReidentifyingOrgsAll
from privacykpis.consts import TOKEN_LOCATION, ORIGIN
from privacykpis.tokenizing import TokenKey, TokenLocation, TokenValue

# Function that returns True if the value is matches the filter
# criteria and should be included in the analysis.
FilterFunc = Callable[[TokenKey, TokenValue, TokenLocation], bool]


def length(key: TokenKey, value: TokenValue,
           loc: TokenLocation, min_length: int = 1) -> bool:
    return len(value) >= min_length


# filter for ISO8601, RFC3339, RSS, W3C, ATOM, COOKIE, RFC2822, RFC850,
# RFC1036, RFC1123, RFC822 date formats
def dates(key: TokenKey, value: TokenValue, loc: TokenLocation) -> bool:
    if value.count("-") < 2 and (value.count("/") < 2 and
                                 value.count(":") < 2):
        return False
    try:
        dateutil.parser.parse(value)
        return True
    except (ValueError, OverflowError):
        return False


def filetypes(key: TokenKey, value: TokenValue, loc: TokenLocation) -> bool:
    (mimetype, _) = mimetypes.guess_type(value)
    return mimetype is None


def should_include_token(key: TokenKey, value: TokenValue,
                         loc: TokenLocation,
                         filters: List[FilterFunc]) -> bool:
    return all([func(key, value, loc) for func in filters])


def kp_exists_in_control(control_reid_all: Optional[ReidentifyingOrgsAll],
                         this_tp: str,  this_k: TokenKey, this_v: TokenValue,
                         this_org: str, this_tk_loc: TokenLocation) -> bool:
    if control_reid_all is None or this_tp not in control_reid_all:
        return False
    ctrl_kp = control_reid_all[this_tp]
    if (this_k in ctrl_kp) and (this_v in ctrl_kp[this_k] and ctrl_kp
                                [this_k][this_v][TOKEN_LOCATION] == this_tk_loc
                                and this_org in ctrl_kp[this_k][this_v][ORIGIN]
                                ):
        return True
    return False
