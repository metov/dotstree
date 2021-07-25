import os
from unittest.mock import Mock
from dotstree.main import install_symlink, q
from pytest import fixture


@fixture(autouse=True)
def questionary_yes(monkeypatch):
    mock_ask = Mock(return_value=True)
    monkeypatch.setattr(q, "confirm", Mock(return_value=mock_ask))


@fixture
def origin(tmp_path):
    return tmp_path / "origin"


@fixture
def target(tmp_path):
    return tmp_path / "target"


@fixture
def other_target(tmp_path):
    return tmp_path / "another-target"


def test_clean_location(origin, target):
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
    file_contents = "contents"
    origin.write_text(file_contents)
    install_symlink(origin, target)
    assert origin.is_symlink()
    assert os.readlink(origin) == str(target)


def test_existing_dir(origin, target):
    origin.mkdir()
    install_symlink(origin, target)
    assert origin.is_symlink()
    assert os.readlink(origin) == str(target)
    assert target.is_dir()
