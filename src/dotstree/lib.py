import os
import subprocess
from pathlib import Path
from typing import List

import yaml
from dotstree import log

SPEC_FILENAMES = ["spec.yaml", "spec.yml"]


def find_specs(p: Path):
    """
    Find and return the parent directory of every spec. Recursive, but terminates
    early -- if you have both:

    ./foo/spec.yaml
    ./foo/bar/spec.yaml
    ./baz/fizz/spec.yml

    Only ./foo and ./baz/fizz will be returned but not ./foo/bar.

    :param p: Path to root of directory tree.
    """
    candidates = [p / fn for fn in SPEC_FILENAMES]
    matches = [ps for ps in candidates if ps.exists()]

    if len(matches) > 0:
        if len(matches) > 1:
            log.warning(f"Multiple specs in {p}")
        ps = matches[0]
        log.debug(f"Found spec at: {ps}")
        return [ps]
    else:
        log.debug(f"No specs directly under {p}")
        child_specs = []
        for pd in p.iterdir():
            if not pd.is_dir():
                continue

            if pd.stem == ".git":
                log.debug(f"Skipping {pd}")
                continue

            child_specs.extend(find_specs(pd))
        return child_specs


def normalize_symlinks(origin, target, spec_path: Path):
    """
    In dotstree, all paths in the spec are either absolute (if starting with /) or
    relative to the location of the spec.yaml file itself. Normalizing means
    disambiguating them by replacing the relative paths with absolute.
    """
    ln = {}
    ln["from"] = Path(origin)
    p = spec_path.parent / target
    ln["to"] = p.resolve()
    return ln


def load_spec_tree(p: Path):
    files = find_specs(p)

    spec = {}
    for ps in files:
        k = str(ps.relative_to(p).parent)
        v = yaml.safe_load(ps.open())

        # Empty YAMLs get loaded as None, not dict
        if not isinstance(v, dict):
            if v is None:
                log.warning(f"{ps} is empty.")
                v = {}
            else:
                log.error(f"{ps} is not a YAML dictionary, skipping.")
                continue

        # Normalize symlinks
        if "symlinks" in v:
            rawlinks = v["symlinks"]
            v["symlinks"] = []
            for ln in rawlinks:
                v["symlinks"].append(normalize_symlinks(ln["from"], ln["to"], ps))

        # Record full path
        if "path" in v:
            log.warning(f'{ps} already contains a "path" key - it will be ignored.')
        v["path"] = ps.parent

        spec[k] = v
    return spec


def combine_spec_trees(paths: List[Path]):
    raise NotImplementedError()


def check_symlink(origin: Path, target: Path):
    """True iff symlink exists at origin and points to destination."""
    if not origin.exists():
        log.debug(f"{origin} doesn't exist.")
        return False

    if not origin.is_symlink():
        log.debug(f"{origin} is not a symlink.")
        return False

    # There is a Path.readlink, but unfortunately Python >=3.9 only :(
    actual = Path(os.readlink(origin)).resolve()
    if not target == actual:
        log.info(
            f"Wrong symlink at {origin}\n"
            f"actual:   {os.readlink(origin)}\n"
            f"expected: {target}"
        )
        return False

    return True


def run_command(cmd, workdir, capture_output=True):
    log.debug(f"Running {cmd}")
    return subprocess.run(cmd, shell=True, capture_output=capture_output, cwd=workdir)
