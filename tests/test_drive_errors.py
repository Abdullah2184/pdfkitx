import pytest
from types import SimpleNamespace
import builtins
import drive_manager.drive_parser as dp


def test_get_service_auth_failure_prints(monkeypatch, capsys):
    def fake_auth():
        raise Exception("no creds")

    monkeypatch.setattr(dp, 'authenticate_drive', fake_auth)
    # call get_service which should catch and print
    svc = dp.get_service()
    captured = capsys.readouterr()
    assert svc is None
    assert 'Failed to authenticate Drive' in captured.out


def test_handle_drive_upload_invalid_path_prints(capsys):
    dp.handle_drive_upload(['nonexistent.file'])
    captured = capsys.readouterr()
    assert 'Invalid path' in captured.out


def test_handle_drive_upload_service_unavailable(monkeypatch, capsys):
    monkeypatch.setattr(dp, 'get_service', lambda: None)
    dp.handle_drive_upload(['somefile.txt'])
    captured = capsys.readouterr()
    assert 'Drive service unavailable' in captured.out
