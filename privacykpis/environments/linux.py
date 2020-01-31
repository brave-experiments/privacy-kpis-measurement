import os
from pathlib import Path
import shutil
import subprocess

from privacykpis.args import Args
from privacykpis.consts import LEAF_CERT


DEBIAN_CERT_DIR = Path("/usr/local/share/ca-certificates")
DEBIAN_CERT_DEST_PATH = DEBIAN_CERT_DIR / Path("mitmproxy.crt")


def setup_env(args: Args):
  DEBIAN_CERT_DIR.mkdir(0o755, exist_ok=True)
  shutil.copyfile(str(LEAF_CERT), str(DEBIAN_CERT_DEST_PATH))
  os.chmod(str(DEBIAN_CERT_DEST_PATH), 0o644)
  subprocess.run(["sudo", "update-ca-certificates"], check=True)

def teardown_env(args: Args):
  shutil.rmtree(str(DEBIAN_CERT_DIR))
  subprocess.run(["sudo", "update-ca-certificates"], check=True)