import builtins
import os
from pathlib import Path
import pytest

import drive_manager.drive_parser as dp


def test_handle_drive_upload_file(monkeypatch, tmp_path):
    f = tmp_path / "doc.pdf"
    f.write_text("pdf")

    called = {}

    def fake_get_service():
        return object()

    def fake_find_folder_by_name(svc, name):
        return False

    def fake_create_folder(svc, name):
        called['create_folder'] = name

    def fake_upload_file(svc, file_path, drive_folder=None):
        called['upload'] = (str(file_path), drive_folder)

    monkeypatch.setattr(dp, 'get_service', fake_get_service)
    monkeypatch.setattr(dp, 'find_folder_by_name', fake_find_folder_by_name)
    monkeypatch.setattr(dp, 'create_folder', fake_create_folder)
    monkeypatch.setattr(dp, 'upload_file', fake_upload_file)

    dp.handle_drive_upload([str(f), "MyFolder"])

    assert 'upload' in called
    assert called['upload'][0].endswith('doc.pdf')
    assert called['create_folder'] == 'MyFolder'


def test_handle_drive_download_and_share(monkeypatch, tmp_path):
    called = {}

    def fake_get_service():
        return object()

    def fake_find_file_id(svc, name):
        return 'FILEID'

    def fake_download_file(svc, file_id, dest):
        called['download'] = (file_id, dest)

    def fake_share_file(svc, file_id, role='reader', anyone=True, email=None):
        called['share'] = (file_id, role, anyone, email)

    monkeypatch.setattr(dp, 'get_service', fake_get_service)
    monkeypatch.setattr(dp, 'find_file_id', fake_find_file_id)
    monkeypatch.setattr(dp, 'download_file', fake_download_file)
    monkeypatch.setattr(dp, 'share_file', fake_share_file)

    dest = tmp_path / "downloads"
    dp.handle_drive_download(['somefile.pdf', str(dest)])
    assert called['download'][0] == 'FILEID'

    dp.handle_drive_share(['somefile.pdf', 'u@example.com'])
    assert called['share'][0] == 'FILEID'
    assert called['share'][3] == 'u@example.com'


def test_logout_removes_token_and_user(monkeypatch, tmp_path):
    # create dummy token and user files
    token = tmp_path / 'token.pickle'
    token.write_bytes(b'data')
    user = tmp_path / 'drive_user.txt'
    user.write_text('me')

    # monkeypatch cwd to tmp_path to simulate project root
    monkeypatch.chdir(tmp_path)

    from drive_manager.drive_parser import logout_drive_session

    logout_drive_session()

    assert not token.exists()
    assert not user.exists()


def test_list_drive_items_prints(monkeypatch, capsys):
    class FakeFilesList:
        def __init__(self, files):
            self._files = files

        def execute(self):
            return {'files': self._files}

    class FakeFiles:
        def list(self, **kwargs):
            return FakeFilesList([{'id': '1', 'name': 'file1.pdf'}])

    class FakeService:
        def files(self):
            return FakeFiles()

    monkeypatch.setattr(dp, 'get_service', lambda: FakeService())
    monkeypatch.setattr(dp, 'list_folders', lambda svc: None)

    dp.list_drive_items()
    captured = capsys.readouterr()
    assert 'Top-level files:' in captured.out
    assert 'file1.pdf' in captured.out


def test_init_drive_session_with_fake_service(fake_drive_service, monkeypatch, capsys, tmp_path):
    # ensure we start in a temp directory so no real files are touched
    monkeypatch.chdir(tmp_path)
    import drive_manager.drive_parser as dp

    dp.init_drive_session('tester')
    captured = capsys.readouterr()
    assert 'Drive session initialized.' in captured.out
    assert dp.service is not None
    # username should be written
    assert (tmp_path / 'drive_user.txt').read_text() == 'tester'


def test_init_drive_session_handles_missing_credentials(monkeypatch, capsys):
    import drive_manager.drive_parser as dp

    # simulate authenticate_drive raising FileNotFoundError (missing credentials.json)
    monkeypatch.setattr(dp, 'authenticate_drive', lambda: (_ for _ in ()).throw(FileNotFoundError('credentials not found')))
    dp.init_drive_session()
    captured = capsys.readouterr()
    assert 'Failed to initialize Drive session' in captured.out
