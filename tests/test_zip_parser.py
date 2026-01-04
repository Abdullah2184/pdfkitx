import os
from zip_manager.zip_parser import add_to_zip, extract_from_zip, remove_from_zip, search_file, REGISTRY_SHELVE
from pathlib import Path
import zipfile


def test_zip_add_extract_remove(tmp_path):
    # Create files to zip
    folder = tmp_path / "f"
    folder.mkdir()
    a = folder / "a.txt"
    b = folder / "b.txt"
    a.write_text("A")
    b.write_text("B")

    archive = tmp_path / "test.zip"
    # pass empty index to let the function create a per-archive index and register the archive
    add_to_zip(str(archive), "", str(folder), file_info={"book_name": "sample"})
    # Check files in archive
    with zipfile.ZipFile(archive, 'r') as zf:
        names = zf.namelist()
        assert any('a.txt' in n for n in names)

    # Extract
    extracted = extract_from_zip(str(archive), target_dir=str(tmp_path / "extracted"))
    assert (extracted / 'a.txt').exists()

    # Remove a file
    # remove uses the archive member filename (relative path)
    # find a matching member name
    member = None
    with zipfile.ZipFile(archive, 'r') as zf:
        member = zf.namelist()[0]
    # remove via default index resolution
    remove_from_zip(str(archive), "", member)
    with zipfile.ZipFile(archive, 'r') as zf:
        assert member not in zf.namelist()

    # registry should reflect archive and now have zero members
    import shelve
    with shelve.open(REGISTRY_SHELVE) as reg:
        assert str(archive) in reg
        entry = reg[str(archive)]
        assert member not in entry.get("members", [])


def test_zip_archives_cmd(tmp_path, capsys):
    # create an archive and ensure 'zip archives' lists it
    folder = tmp_path / "f2"
    folder.mkdir()
    (folder / "x.txt").write_text("X")
    archive = tmp_path / "test2.zip"
    add_to_zip(str(archive), "", str(folder), file_info={"tag": "t"})

    from zip_manager.zip_parser import handle_zip_command
    # list archives (no second arg)
    handle_zip_command(["list"])
    captured = capsys.readouterr()
    assert str(archive) in captured.out

    # list contents of the specific archive (by archive path)
    handle_zip_command(["list", str(archive)])
    captured2 = capsys.readouterr()
    # ensure it lists member filenames such as x.txt
    assert any('x.txt' in line for line in captured2.out.splitlines())


def test_add_nonexistent_target_raises(tmp_path):
    archive = tmp_path / "nope.zip"
    missing = tmp_path / "does_not_exist"
    from zip_manager.zip_parser import add_to_zip

    try:
        add_to_zip(str(archive), "", str(missing))
        raised = False
    except FileNotFoundError:
        raised = True

    assert raised


def test_remove_nonexistent_member_raises(tmp_path):
    folder = tmp_path / "f3"
    folder.mkdir()
    (folder / "a.txt").write_text("A")
    archive = tmp_path / "test3.zip"
    add_to_zip(str(archive), "", str(folder), file_info={"k":"v"})

    from zip_manager.zip_parser import remove_from_zip
    import pytest

    with pytest.raises(KeyError):
        remove_from_zip(str(archive), "", "not_in_archive.txt")


def test_list_nonexistent_archive_shows_message(capsys):
    from zip_manager.zip_parser import handle_zip_command

    handle_zip_command(["list", "nonexistent.zip"])
    captured = capsys.readouterr()
    assert "Archive not found" in captured.out
