import os
from pathlib import Path, PurePath

THIS_PATH = os.path.realpath(__file__)

RESOURCES_PATH = Path(THIS_PATH, "..", "..", "resources").resolve()
CERT_PATH = RESOURCES_PATH / Path("certs")
LEAF_CERT = CERT_PATH / Path("mitmproxy-ca-cert.cer")
LOG_HEADERS_SCRIPT_PATH = RESOURCES_PATH / Path("scripts", "log_headers.py")