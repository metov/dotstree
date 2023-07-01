from unittest.mock import Mock

from dotstree import main
from dotstree.main import check_symlinks_status
from pytest import fixture


def mock_symlink_is_correct(monkeypatch, results):
    m = Mock(side_effect=results)
    monkeypatch.setattr(main, "symlink_is_correct", m)

    symlinks = [{"from": "mock/from", "to": "mock/to"}] * len(results)
    return {"symlinks": symlinks}


@fixture
def correct_symlink(monkeypatch):
    return mock_symlink_is_correct(monkeypatch, [True])


@fixture
def wrong_symlink(monkeypatch):
    return mock_symlink_is_correct(monkeypatch, [False])


@fixture
def mixed_symlinks(monkeypatch):
    return mock_symlink_is_correct(monkeypatch, [True, False])


def test_no_symlinks():
    spec = {}
    status = check_symlinks_status(spec)
    assert status == None


def test_empty_symlinks():
    spec = {"symlinks": []}
    status = check_symlinks_status(spec)
    assert status == True


def test_correct_symlink(correct_symlink):
    status = check_symlinks_status(correct_symlink)
    assert status == True


def test_wrong_symlink(wrong_symlink):
    status = check_symlinks_status(wrong_symlink)
    assert status == False


def test_mixed_symlink(mixed_symlinks):
    status = check_symlinks_status(mixed_symlinks)
    assert status == False
