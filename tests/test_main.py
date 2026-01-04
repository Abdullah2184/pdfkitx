import builtins
from pathlib import Path

import pytest

import commands


def test_main_starts_repl_when_no_args(monkeypatch):
    called = {}

    import main as app_main

    def fake_run_repl(parser):
        called['parser'] = parser

    monkeypatch.setattr(app_main, 'run_repl', fake_run_repl)
    rc = app_main.main([])
    assert rc == 0
    assert 'parser' in called


def test_main_one_shot_executes_command(monkeypatch):
    called = {}

    def fake_drive(tokens):
        called['tokens'] = tokens

    monkeypatch.setattr(commands, 'handle_drive_command', fake_drive)

    import main as app_main
    rc = app_main.main(['drive', 'share', 'myfile', 'me@example.com'])
    assert rc == 0
    assert called['tokens'] == ['share', 'myfile', 'me@example.com']


def test_main_returns_nonzero_on_parse_error():
    import main as app_main
    # missing subcommand for 'drive' should produce a non-zero exit code
    rc = app_main.main(['drive'])
    assert rc != 0


def test_run_subcommand_executes_script(monkeypatch, tmp_path):
    called = []

    def fake_pdf(tokens):
        called.append(tokens)

    monkeypatch.setattr(commands, 'handle_pdf_command', fake_pdf)
    script = tmp_path / "cmds.txt"
    script.write_text("# comment\npdf split my.pdf 1-2 --delete\n")

    import main as app_main
    rc = app_main.main(['run', str(script)])
    assert rc == 0
    assert any(t[0] == 'split' for t in called)
