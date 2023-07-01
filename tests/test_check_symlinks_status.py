from unittest.mock import Mock

from dotstree import main
from dotstree.main import check_symlinks_status
from pytest import fixture


def mock_symlink_is_correct(monkeypatch, results):
    m = Mock(side_effect=results)
    monkeypatch.setattr(main, "symlink_is_correct", m)


@fixture
def correct_symlink(monkeypatch):
    mock_symlink_is_correct(monkeypatch, [True])


@fixture
def wrong_symlink(monkeypatch):
    mock_symlink_is_correct(monkeypatch, [False])


@fixture
def mixed_symlinks(monkeypatch):
    mock_symlink_is_correct(monkeypatch, [True, False])


def test_no_symlinks():
    spec = {}
    status = check_symlinks_status(spec)
    assert status == None


def test_empty_symlinks():
    spec = {"symlinks": []}
    status = check_symlinks_status(spec)
    assert status == True


def test_correct_symlink(correct_symlink):
    spec = {"symlinks": [{"from": "mock/from", "to": "mock/to"}]}
    status = check_symlinks_status(spec)
    assert status == True


def test_wrong_symlink(wrong_symlink):
    spec = {"symlinks": [{"from": "mock/from", "to": "mock/to"}]}
    status = check_symlinks_status(spec)
    assert status == False


def test_mixed_symlink(mixed_symlinks):
    spec = {
        "symlinks": [
            {"from": "mock/from", "to": "mock/to"},
            {"from": "mock/from", "to": "mock/to"},
        ]
    }
    status = check_symlinks_status(spec)
    assert status == False
