from dotstree.main import status_icon


def test_success():
    assert status_icon(True) == "🟢"


def test_failure():
    assert status_icon(False) == "🔴"


def test_none():
    assert status_icon(None) == "⚪"
