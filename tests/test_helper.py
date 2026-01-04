import pytest
from helper import resolve_path
from pathlib import Path


def test_resolve_path_missing(tmp_path):
    missing = tmp_path / "no_such_file.txt"
    with pytest.raises(FileNotFoundError):
        resolve_path(str(missing))


def test_resolve_path_existing(tmp_path):
    f = tmp_path / "exists.txt"
    f.write_text("hi")
    resolved = resolve_path(str(f))
    assert Path(resolved).exists()
