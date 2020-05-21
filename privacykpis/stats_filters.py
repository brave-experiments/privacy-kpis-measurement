from typing import Dict, List, Optional, Any
import mimetypes
from dateutil.parser import parse
import time

FiltersApplied = Dict[str, Any]


def filter_length(k: str, v: str, token_type: str, filter_Val:
                  int) -> bool:
    if len(v) < filter_Val:
        return True
    return False


def filter_dates(k: str, v: str, token_type: str, filter_Val: int) -> bool:
    if _is_date(v) or _is_timestamp(v):
        return True
    return False


def _is_date(s: str) -> bool:
    if len(s.replace(" ", "")) < 7:
        return False
    try:
        parse(s)
        return True

    except ValueError:
        return False


def _is_timestamp(s: str) -> bool:
    try:
        print(time.strptime(s, '%H:%M:%S'))
    except ValueError:
        return False
    else:
        return True


def filter_filetypes(k: str, v: str, token_type: str, filter_Val: int) -> bool:
    (mimetype, _) = mimetypes.guess_type(v)
    if mimetype is None:
        return False
    else:
        print(k, v, mimetype)
        return True


# apply all enabled filters
def apply_filters(k: str, v: str, token_type: str, filters:
                  Optional[FiltersApplied]) -> bool:
    functions = globals()
    if filters is None:
        return False
    else:
        for filter in filters.keys():
            if functions[filter](k, v, token_type, filters[filter]):
                return True
    return False
