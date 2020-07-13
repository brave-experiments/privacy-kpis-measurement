import datetime
import mimetypes
from typing import Union

import calendar
import dateutil.parser


def is_datetime(token: str) -> bool:
    if len(token) < 10:
        return False

    if isinstance(token, str):
        try:
            dateutil.parser.parse(token)
            return True
        except (dateutil.parser.ParserError, OverflowError,  # type: ignore
                calendar.IllegalMonthError, TypeError):
            return False

    float_token = None
    try:
        float_token = float(token)
    except ValueError:
        return False

    # Otherwise check and see if this looks like a numberic encoding of a
    # timestamp.
    year_start_ts = 1577836800
    year_end_ts = 1609459200
    if float_token > year_start_ts and float_token < year_end_ts:
        return True

    year_start_ts_ms = 1577836800000
    year_end_ts_ms = 1609459200000
    # Next, see if it looks like a millisecond timestamp
    if float_token > year_start_ts_ms and float_token < year_end_ts_ms:
        return True

    # Finally, filter out relative timestamps (like from performance.now).
    if float_token and float_token < 10000000:
        return True

    return False


def is_short(token: str, min_length: int = 11) -> bool:
    token_str = token if isinstance(token, str) else str(token)
    return len(token_str) < min_length


def is_url(token: str) -> bool:
    return token.startswith("http://") or token.startswith("https://")


def is_filename(token: str) -> bool:
    (mimetype, _) = mimetypes.guess_type(token)
    return mimetype is not None


def should_ignore_token(token: str) -> bool:
    if is_datetime(token):
        return True
    if is_short(token):
        return True
    if is_url(token):
        return True
    if is_filename(token):
        return True
    return False
