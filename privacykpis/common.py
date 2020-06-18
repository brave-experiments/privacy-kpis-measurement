import os
import pathlib
import platform
import sys
from typing import Optional, TYPE_CHECKING


def err(msg: str) -> None:
    print(msg, file=sys.stderr)


def get_real_user() -> str:
    return pathlib.Path.home().owner()


def is_root() -> bool:
    return os.geteuid() == 0
