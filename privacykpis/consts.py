import os
from pathlib import Path, PurePath

THIS_PATH = os.path.realpath(__file__)

SUPPORTED_BROWSERS = ("safari", "chrome", "firefox")
RESOURCES_PATH = Path(THIS_PATH, "..", "..", "resources").resolve()
CERT_PATH = RESOURCES_PATH / Path("certs")
LEAF_CERT = CERT_PATH / Path("mitmproxy-ca-cert.cer")
LOG_HEADERS_SCRIPT_PATH = RESOURCES_PATH / Path("scripts", "log_headers.py")

DEFAULT_FIREFOX_PROFILE = RESOURCES_PATH / Path("profiles/firefox")

CHROME_POLICY_PATH = RESOURCES_PATH / Path("misc", "chrome_policy.json")

DEFAULT_PROXY_HOST = "127.0.0.1"
DEFAULT_PROXY_PORT = 8888

URL = "url"
TIMESTAMP = "timestamp"
ORIGIN = "origin"
TOKEN_LOCATION = "token_location"
TOKEN_KEY = "token_key"
TOKEN_VALUE = "token_value"
SITE = "site"
REQUESTED_ETLD1 = "requested etld+1"
NODE_TYPE = "type"
