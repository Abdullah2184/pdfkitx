"""Test helpers and environment setup for pytest.

Ensure the project root is on sys.path so tests can import project modules
as top-level packages (e.g., `commands`, `drive_manager`). This is a
portable approach that works regardless of how pytest determines its
working directory during collection.
"""
from __future__ import annotations
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Insert at front so tests import local package versions, not installed ones
    sys.path.insert(0, str(ROOT))

import pytest


@pytest.fixture
def fake_drive_service(monkeypatch):
    """Fixture that fakes Google Drive authentication and returns a
    lightweight fake service object for tests that need Drive functionality.

    It monkeypatches the authenticate_drive function used by
    `drive_manager.drive_parser` so that tests never invoke real OAuth.
    """
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

    fake = FakeService()
    # patch the authenticate entry used by drive_parser
    import drive_manager.drive_parser as dp
    monkeypatch.setattr(dp, 'authenticate_drive', lambda: fake)
    yield fake


@pytest.fixture(autouse=True)
def disable_real_drive_auth(monkeypatch):
    """Automatically prevent any test from invoking real Google OAuth.

    This autouse fixture monkeypatches both `drive_manager.drive_auth.authenticate_drive`
    and the `authenticate_drive` reference in `drive_manager.drive_parser` so tests
    cannot accidentally run the real OAuth flow. Individual tests may override
    this behavior by patching these attributes themselves.
    """
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

    fake = FakeService()

    import drive_manager.drive_auth as da
    import drive_manager.drive_parser as dp

    monkeypatch.setattr(da, 'authenticate_drive', lambda: fake)
    monkeypatch.setattr(dp, 'authenticate_drive', lambda: fake)
    yield
