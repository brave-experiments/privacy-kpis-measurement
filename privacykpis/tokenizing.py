from enum import Enum
import json
import http.cookies
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import parse_qsl, urlparse


class BodyDataEncoding(Enum):
    UNKNOWN = 1
    JSON = 2
    FORM_URL_ENC = 3
    FORM_MULTIPART = 4


KeyValueList = List[Tuple[str, str]]


class RecordParseResult:
    cookies: Optional[KeyValueList] = None
    path: Optional[KeyValueList] = None
    query: Optional[KeyValueList] = None
    body: Optional[KeyValueList] = None
    body_encoding: BodyDataEncoding = BodyDataEncoding.UNKNOWN


def guess_body_format(header_content_type: str) -> BodyDataEncoding:
    if header_content_type.startswith("application/json"):
        return BodyDataEncoding.JSON
    if header_content_type.startswith("text/json"):
        return BodyDataEncoding.JSON
    if header_content_type.startswith("application/x-www-form-urlencoded"):
        return BodyDataEncoding.FORM_URL_ENC
    if header_content_type.startswith("multipart/form-data"):
        return BodyDataEncoding.FORM_MULTIPART
    return BodyDataEncoding.UNKNOWN


def from_record(record: Dict[str, Any]) -> RecordParseResult:
    result = RecordParseResult()

    body_encoding = BodyDataEncoding.UNKNOWN
    for name, value in record["headers"]:
        lower_header = name.lower()
        if lower_header == "cookie":
            result.cookies = kvs_from_cookies(value)
            continue
        if lower_header == "content-type":
            body_encoding = guess_body_format(value)
            continue

    parsed_url = urlparse(record["url"])
    if parsed_url.path:
        result.path = kvs_from_url_path(parsed_url.path)

    if parsed_url.query:
        result.query = kvs_from_url_query(parsed_url.query)

    result.body = kvs_from_body(body_encoding, record["body"])
    result.body_encoding = body_encoding
    return result


def kvs_from_cookies(cookie_header: str) -> KeyValueList:
    try:
        cookies: Any = http.cookies.SimpleCookie(cookie_header)
        return [(k, v.value) for k, v in cookies.items()]
    except http.cookies.CookieError:
        return []


def kvs_from_url_path(url_path: str) -> KeyValueList:
    path_parts = url_path.strip(" /").split("/")
    return [(str(i), p) for i, p in enumerate(path_parts)]


def kvs_from_url_query(url_query: str) -> KeyValueList:
    return parse_qsl(url_query)


def kvs_from_json_str(body: str) -> Optional[KeyValueList]:
    try:
        json_data = json.loads(body)
    except json.JSONDecodeError:
        return None

    if json_data is None:
        return None

    kvs: List[Tuple[str, str]] = []

    if type(json_data) is list:
        if len(json_data) == 0:
            return kvs
        if type(json_data[0]) is not dict:
            return kvs
        json_data = json_data[0]

    if len(json_data.keys()) == 0:
        return None

    for key, value in json_data.items():
        if isinstance(value, str):
            kvs.append((key, value))
        else:
            kvs.append((key, json.dumps(value)))
    return kvs


def kvs_from_body(body_format: BodyDataEncoding,
                  body: str) -> Optional[KeyValueList]:
    if body_format == BodyDataEncoding.JSON:
        return kvs_from_json_str(body)
    if body_format == BodyDataEncoding.UNKNOWN:
        return kvs_from_json_str(body)
    if body_format == BodyDataEncoding.FORM_URL_ENC:
        return parse_qsl(body)
    if body_format == BodyDataEncoding.FORM_MULTIPART:
        return None
    return None
