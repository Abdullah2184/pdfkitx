import builtins
from pathlib import Path
import tempfile

import pytest

import commands
from commands import make_parser, parse_line_and_execute


def test_pdf_split_calls_handler(monkeypatch):
    called = {}

    def fake_pdf(tokens):
        called['tokens'] = tokens

    monkeypatch.setattr(commands, 'handle_pdf_command', fake_pdf)
    parser = make_parser()
    ns = parser.parse_args(['pdf', 'split', 'doc.pdf', '1-3,5', '--delete'])
    assert hasattr(ns, 'func')
    ns.func(ns)
    assert called['tokens'] == ['split', 'doc.pdf', '1-3,5', 'delete']


def test_drive_share_args(monkeypatch):
    called = {}

    def fake_drive(tokens):
        called['tokens'] = tokens

    monkeypatch.setattr(commands, 'handle_drive_command', fake_drive)
    parser = make_parser()
    ns = parser.parse_args(['drive', 'share', 'myfile', 'me@example.com'])
    ns.func(ns)
    assert called['tokens'] == ['share', 'myfile', 'me@example.com']


def test_parse_line_and_execute(monkeypatch, tmp_path):
    called = {}

    def fake_zip(tokens):
        called['tokens'] = tokens

    monkeypatch.setattr(commands, 'handle_zip_command', fake_zip)
    parser = make_parser()
    # test quoted member names and dest
    parse_line_and_execute('zip extract archive.zip dest_dir file1.txt file2.txt', parser)
    assert called['tokens'][0] == 'extract'


def test_script_runner_executes_lines(monkeypatch, tmp_path):
    called = []

    def fake_pdf(tokens):
        called.append(tokens)

    monkeypatch.setattr(commands, 'handle_pdf_command', fake_pdf)
    script = tmp_path / "cmds.txt"
    script.write_text("# comment\npdf split my.pdf 1-2 --delete\n")
    parser = make_parser()
    ns = parser.parse_args(['run', str(script)])
    ns.func(ns)
    assert any(t[0] == 'split' for t in called)
