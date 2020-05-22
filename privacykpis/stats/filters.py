import mimetypes
import time
from typing import Any, Callable, Dict, List, Optional

import dateutil.parser

from privacykpis.tokenizing import TokenKey, TokenLocation, TokenValue

# Function that returns True if the value is matches the filter
# critera and should be included in the analysis.
FilterFunc = Callable[[TokenKey, TokenValue, TokenLocation], bool]


def length(key: TokenKey, value: TokenValue,
           loc: TokenLocation, min_length: int = 1) -> bool:
    return len(value) >= min_length


# filter for ISO8601, RFC3339, RSS, W3C, ATOM, COOKIE, RFC2822, RFC850,
# RFC1036, RFC1123, RFC822 date formats
def dates(key: TokenKey, value: TokenValue, loc: TokenLocation) -> bool:
    try:
        dateutil.parser.parse(value)
        return True
    except ValueError:
        return False


def filetypes(key: TokenKey, value: TokenValue, loc: TokenLocation) -> bool:
    (mimetype, _) = mimetypes.guess_type(value)
    return mimetype is not None


def should_include_token(key: TokenKey, value: TokenValue,
                         loc: TokenLocation,
                         filters: List[FilterFunc]) -> bool:
    return all([func(key, value, loc) for func in filters])
