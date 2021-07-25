import os
from pathlib import Path
from unittest.mock import Mock
from pytest import fixture

from dotstree.main import install_symlink


@fixture
def origin(tmp_path):
    return tmp_path / "origin"


@fixture
def target(tmp_path):
    return tmp_path / "target"


@fixture
def other_target(tmp_path):
    return tmp_path / "another-target"


def test_no_existing(origin, target):
    install_symlink(origin, target)
    assert origin.is_symlink()
    assert os.readlink(origin) == str(target)


def test_existing_symlink_correct(origin, target):
    origin.symlink_to(target)
    install_symlink(origin, target)
    assert origin.is_symlink()
    assert os.readlink(origin) == str(target)


def test_existing_symlink_wrong(origin, target, other_target):
    origin.symlink_to(other_target)
    install_symlink(origin, target)
    assert origin.is_symlink()
    assert os.readlink(origin) == str(target)


def test_existing_file(origin, target):
    origin.write_text("contents")
    install_symlink(origin, target)
    assert origin.is_symlink()
    assert os.readlink(origin) == str(target)


def test_existing_dir(origin, target):
    origin.mkdir()
    install_symlink(origin, target)
    assert origin.is_symlink()
    assert os.readlink(origin) == str(target)
