import builtins
import pytest
from commands import make_parser
from repl import run_repl


def test_repl_continues_on_parse_error(monkeypatch):
    # provide a bad command and then exit; ensure no exception
    inputs = iter(['pdf split', 'exit'])

    def fake_input(prompt=''):
        return next(inputs)

    monkeypatch.setattr(builtins, 'input', fake_input)
    parser = make_parser()
    # Should not raise
    run_repl(parser)
