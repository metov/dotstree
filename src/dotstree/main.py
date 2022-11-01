"""
Flexible dotfile manager based on directory trees. Runs against a directory tree
containing program specs.

For details, see: https://www.github.com/metov/doststree

Usage:
    dots (-h | --help)
    dots [options] install PATH
    dots [options] check PATH

Options:
    --log LEVEL  Minimum level of logs to print [default: INFO]
"""
import logging
import os
import shutil
from operator import itemgetter
from pathlib import Path
from time import time

import questionary as q
from docopt import docopt
from metovlogs import get_log
from tabulate import tabulate
from tqdm import tqdm

from .lib import load_spec_tree, run_command, symlink_is_correct

log = get_log(__name__)


def main():
    args = docopt(__doc__, options_first=True)

    if level := args["--log"]:
        log.setLevel(logging.getLevelName(level.upper()))

    log.debug(f"Arguments:\n{args}")

    tree = Path(args["PATH"]) or Path()
    spec = load_spec_tree(tree)

    if args["install"]:
        install_specs(spec)
    elif args["check"]:
        check_specs(spec)
    else:
        log.critical("Unexpected arguments")


def check_specs(all_specs):
    status = []
    for name, spec in tqdm(all_specs.items()):

        layer, _, spec_name = name.rpartition("/")
        res = {"Layer": layer, "Spec": spec_name}

        t1 = time()
        res["Symlinks"] = "⚪"
        if "symlinks" in spec:
            res["Symlinks"] = "🟢"
            for ln in spec.get("symlinks"):
                origin = Path(ln["from"]).expanduser()
                target = Path(ln["to"])
                if not symlink_is_correct(Path(origin), Path(target)):
                    res["Symlinks"] = "🔴"

        t2 = time()

        res["Program"] = "⚪"
        if "check" in spec:
            result = run_command(spec["check"], spec["path"])
            if result.returncode == 0:
                res["Program"] = "🟢"
            else:
                res["Program"] = "🔴"
                msg = f"Command: {spec['check']}"
                log.info(msg + f"\nStandard error:\n{result.stderr.decode()}")
                log.debug(f"Standard output:\n{result.stdout.decode()}")

        t3 = time()

        res["Symlink time"] = t2 - t1
        res["Check time"] = t3 - t2

        status.append(res)

    # Tweak the sort order for nicer presentation
    status.sort(key=itemgetter("Spec"))
    status.sort(key=itemgetter("Program"), reverse=True)
    status.sort(key=itemgetter("Symlinks"), reverse=True)
    status.sort(key=itemgetter("Layer"))
    status.sort(key=lambda d: d["Layer"] != "")
    print(tabulate(status, headers="keys", floatfmt=".3f"))


def install_specs(all_specs):
    for name, spec in tqdm(all_specs.items()):
        if "symlinks" in spec:
            for ln in spec.get("symlinks"):
                install_symlink(Path(ln["from"]).expanduser(), Path(ln["to"]))

        if "install" in spec:
            if "check" in spec:
                result = run_command("pwd", spec["path"].absolute())
                print(result.stdout.decode())

                result = run_command(spec["check"], spec["path"])
                if result.returncode == 0:
                    log.info(f"Skipping {name} because check command succeeded.")
                    continue

            log.info(f"Installing {name}")
            install_cmd = spec["install"]
            res = run_command(install_cmd, spec["path"], capture_output=False)
            if res.returncode != 0:
                msg = res.stderr.decode() if res.stderr else str(res.stderr)
                log.error(f"{spec['install']} failed with:\n{msg}")


def install_symlink(origin, target):
    if symlink_is_correct(origin, target):
        log.debug(f"Skipping {origin} because it already points to {target}")
        return

    if symlink_exists(origin) or file_exists(origin, target):
        log.debug(f"Skipping {origin}")
        return

    origin.parent.mkdir(parents=True, exist_ok=True)
    log.debug(f"Symlinking {origin} to {target}")
    origin.symlink_to(target)


def symlink_exists(origin):
    if origin.is_symlink():
        target = os.readlink(origin)
        log.warning(f"Origin exists, but points to {target}.")
        if q.confirm(f"Replace {origin}?", default=True).ask():
            log.info(f"Removing {origin}")
            origin.unlink()
        else:
            log.error(f"A symlink already exists at {origin} and points to {target}")
            return True
    return False


def file_exists(origin, target):
    if origin.exists():
        log.warning(f"File exists at {origin}")
        if q.confirm(f"Move {origin} to {target}?", default=True).ask():
            log.info(f"Moving {origin} to {target}")
            shutil.move(origin, target)
        else:
            log.error(f"A file already exists at {origin}")
            return True
    return False
