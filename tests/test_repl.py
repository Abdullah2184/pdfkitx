import builtins

import pytest

import commands
from repl import run_repl


def test_repl_executes_command_and_exits_on_exit(monkeypatch):
    called = {}

    def fake_drive(tokens):
        called['tokens'] = tokens

    monkeypatch.setattr(commands, 'handle_drive_command', fake_drive)

    # Prepare inputs: a valid command, then 'exit' to stop the loop
    inputs = iter(['drive share myfile me@example.com', 'exit'])

    def fake_input(prompt=''):
        return next(inputs)

    monkeypatch.setattr(builtins, 'input', fake_input)

    parser = commands.make_parser()
    run_repl(parser)

    assert called['tokens'] == ['share', 'myfile', 'me@example.com']


def test_repl_handles_quoted_args(monkeypatch):
    called = {}

    def fake_zip(tokens):
        called['tokens'] = tokens

    monkeypatch.setattr(commands, 'handle_zip_command', fake_zip)

    inputs = iter(['zip extract "archive name.zip" "dest dir" "file 1.txt"', 'quit'])

    def fake_input(prompt=''):
        return next(inputs)

    monkeypatch.setattr(builtins, 'input', fake_input)

    parser = commands.make_parser()
    run_repl(parser)

    # first token must be 'extract'
    assert called['tokens'][0] == 'extract'
