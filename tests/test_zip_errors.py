import pytest
from pathlib import Path
import zipfile

from zip_manager.zip_parser import add_to_zip, remove_from_zip, search_file


def test_add_to_zip_nonexistent_target_raises(tmp_path):
    archive = tmp_path / "out.zip"
    with pytest.raises(FileNotFoundError):
        add_to_zip(str(archive), "", str(tmp_path / "nope"))


def test_remove_nonexistent_member_raises(tmp_path):
    # create a zip with one file
    archive = tmp_path / "test.zip"
    (tmp_path / "a.txt").write_text("A")
    add_to_zip(str(archive), "", str(tmp_path / "a.txt"))

    # attempt to remove a missing member
    with pytest.raises(KeyError):
        remove_from_zip(str(archive), "", "missing.txt")


def test_search_returns_empty_on_no_match(tmp_path):
    archive = tmp_path / "t.zip"
    (tmp_path / "a.txt").write_text("A")
    add_to_zip(str(archive), "idx", str(tmp_path / "a.txt"), file_info={'k': 'v'})

    matches = search_file("idx", [("k", "not-found")])
    assert matches == []
