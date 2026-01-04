import os
import pytest
from commands import make_parser


def test_run_subcommand_script_not_found(capsys, tmp_path):
    parser = make_parser()
    ns = parser.parse_args(['run', str(tmp_path / 'nope.txt')])
    ns.func(ns)
    captured = capsys.readouterr()
    assert 'Script not found' in captured.out


def test_run_subcommand_handles_command_errors(monkeypatch, tmp_path, capsys):
    # create script with a bad command that will cause parse errors
    script = tmp_path / 'wf.txt'
    script.write_text('pdf split\n')

    parser = make_parser()
    ns = parser.parse_args(['run', str(script)])
    # run should not raise
    ns.func(ns)
    captured = capsys.readouterr()
    # parse errors are swallowed by parse_line_and_execute (SystemExit)
    assert captured.out == '' or 'usage' in captured.out.lower()
