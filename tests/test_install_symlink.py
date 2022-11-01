import os

from pytest import fixture

from dotstree.main import install_symlink, q


def mock_answer(monkeypatch, result):
    class MockQuestion:
        def __init__(self, _, **kwargs):
            pass

        @staticmethod
        def ask():
            return result

    monkeypatch.setattr(q, "confirm", MockQuestion)


@fixture
def questionary_yes(monkeypatch):
    mock_answer(monkeypatch, True)


@fixture
def questionary_no(monkeypatch):
    mock_answer(monkeypatch, False)


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


def test_existing_symlink_wrong_overwrite(
    origin, target, other_target, questionary_yes
):
    origin.symlink_to(other_target)
    install_symlink(origin, target)
    assert origin.is_symlink()
    assert os.readlink(origin) == str(target)


def test_existing_symlink_wrong_leave(origin, target, other_target, questionary_no):
    origin.symlink_to(other_target)
    install_symlink(origin, target)
    assert origin.is_symlink()

    obs = str(os.readlink(origin))
    exp = str(other_target)
    assert obs == exp


def test_existing_file_move(origin, target, questionary_yes):
    file_contents = "contents"
    origin.write_text(file_contents)
    install_symlink(origin, target)
    assert origin.is_symlink()
    assert os.readlink(origin) == str(target)


def test_existing_file_leave(origin, target, questionary_no):
    origin.touch()
    install_symlink(origin, target)
    assert not origin.is_symlink()


def test_existing_dir_move(origin, target, questionary_yes):
    origin.mkdir()
    install_symlink(origin, target)
    assert origin.is_symlink()
    assert os.readlink(origin) == str(target)
    assert target.is_dir()


def test_existing_dir_leave(origin, target, questionary_no):
    origin.mkdir()
    install_symlink(origin, target)
    assert origin.is_dir()
