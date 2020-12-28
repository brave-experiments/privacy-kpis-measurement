#!/usr/bin/env python3
import argparse
from pathlib import Path
import subprocess

THIS_SCRIPT_PATH = Path(__file__).parent
PROCESS_SCRIPTS_PATH = THIS_SCRIPT_PATH / Path("process")
DEFAULT_CODE_PATH = THIS_SCRIPT_PATH.resolve()

INTERMEDIATE_DIR_NAMES = {"expand", "serialize", "extract", "flatten"}
INTERMEDIATE_DIR_NAMES_CACHE = {k: None for k in INTERMEDIATE_DIR_NAMES}


def output_path_for_step(output_root_dir: Path, step: str) -> Path:
    if INTERMEDIATE_DIR_NAMES_CACHE[step] is not None:
        return INTERMEDIATE_DIR_NAMES_CACHE[step]
    INTERMEDIATE_DIR_NAMES_CACHE[step] = output_root_dir / Path(step)
    return INTERMEDIATE_DIR_NAMES_CACHE[step]


def _make_result_dirs(output_dir: Path) -> None:
    for intermediate_dir_name in INTERMEDIATE_DIR_NAMES:
        intermediate_result_dir_path = output_dir / Path(intermediate_dir_name)
        if intermediate_result_dir_path.is_dir():
            continue
        intermediate_result_dir_path.mkdir()


def _run_expand_py(input_dir: Path, output_dir: Path) -> None:
    expand_output_path = output_path_for_step(output_dir, "expand")
    expand_script_path = PROCESS_SCRIPTS_PATH / Path("expand.py")
    args = [str(expand_script_path), str(input_dir), str(expand_output_path)]
    subprocess.run(args, check=True)


def _run_serialize_fish(code_dir: Path, output_dir: Path,
                        redirect_cache_path: Path) -> None:
    expand_output_path = output_path_for_step(output_dir, "expand")
    serialize_output_path = output_path_for_step(output_dir, "serialize")
    util_serialize_script_path = PROCESS_SCRIPTS_PATH / Path("serialize.fish")
    main_serialize_script_path = code_dir / Path("serialize.py")
    args = [str(util_serialize_script_path), str(main_serialize_script_path),
            str(expand_output_path), str(serialize_output_path),
            "--redirect-cache", str(redirect_cache_path)]
    subprocess.run(args, check=True)


def _run_extract_fish(code_dir: Path, output_dir: Path) -> None:
    serialize_output_path = output_path_for_step(output_dir, "serialize")
    extract_output_path = output_path_for_step(output_dir, "extract")
    util_extract_script_path = PROCESS_SCRIPTS_PATH / Path("extract.fish")
    main_extract_script_path = code_dir / Path("extract.py")
    args = [str(util_extract_script_path), str(main_extract_script_path),
            str(serialize_output_path), str(extract_output_path)]
    subprocess.run(args, check=True)


def _run_flatten_py(output_dir: Path) -> None:
    extract_output_path = output_path_for_step(output_dir, "extract")
    flatten_output_path = output_path_for_step(output_dir, "flatten")
    flatten_script_path = PROCESS_SCRIPTS_PATH / Path("flatten.py")
    for extracted_json_file in extract_output_path.iterdir():
        if extracted_json_file.is_dir():
            continue
        if extracted_json_file.suffix != ".json":
            continue
        args = [str(flatten_script_path), str(extracted_json_file)]
        subprocess.run(args, check=True)


PARSER = argparse.ArgumentParser("Extract tokens from crawl data.")
PARSER.add_argument("-i", "--input", required=True,
                    help="Path to a directory of unprocessed JSON logs.")
PARSER.add_argument("-o", "--output", required=True,
                    help="Directory to write results to (intermediate " +
                         "results are written to sub directories.")
PARSER.add_argument("-c", "--code", default=str(DEFAULT_CODE_PATH),
                    help="Path to the root of the privacy-kpis-measurement " +
                         "directory.")
PARSER.add_argument("--skip-expand", action="store_true",
                    help="If provided, skip the 'expand' step.")
PARSER.add_argument("--skip-serialize", action="store_true",
                    help="If provided, skip the 'serialize' step.")
PARSER.add_argument("--skip-extract", action="store_true",
                    help="If provided, skip the 'extract' step.")
PARSER.add_argument("--skip-flatten", action="store_true",
                    help="If provided, skip the 'flatten' step.")
PARSER.add_argument("--redirect-cache",
                    default="/tmp/privacy-kpis-measurement.cache",
                    help="Where to cache HTTP redirect look ups.")
ARGS = PARSER.parse_args()

INPUT_PATH = Path(ARGS.input)
OUTPUT_PATH = Path(ARGS.output)
CODE_PATH = Path(ARGS.code)

_make_result_dirs(OUTPUT_PATH)
if not ARGS.skip_expand:
    _run_expand_py(INPUT_PATH, OUTPUT_PATH)
if not ARGS.skip_serialize:
    _run_serialize_fish(CODE_PATH, OUTPUT_PATH, Path(ARGS.redirect_cache))
if not ARGS.skip_extract:
    _run_extract_fish(CODE_PATH, OUTPUT_PATH)
if not ARGS.skip_flatten:
    _run_flatten_py(OUTPUT_PATH)
