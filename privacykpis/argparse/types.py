import argparse
import pathlib
import sys
from typing import Optional


def writeable_path(possible_path: Optional[str]) -> str:
    if possible_path is None:
        return possible_path

    tested_path = pathlib.Path(possible_path)
    if tested_path.exists():
        msg = f'cannot write to {possible_path}, file already exists'
        raise argparse.ArgumentTypeError(msg)

    target_dir = tested_path.parent
    if not target_dir.is_dir():
        msg = f'Invalid path to write to, {target_dir} is nnt a directory'
        raise argparse.ArgumentTypeError(msg)

    try:
        tested_path.write_text('test')
        tested_path.unlink()
    except FileNotFoundError as e:
        raise argparse.ArgumentTypeError(e)

    return tested_path