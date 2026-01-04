"""Improved REPL using the shared argparse parser for consistent parsing.

This REPL will accept the same syntax as the CLI. It uses shlex splitting
so quoted arguments are handled correctly.
"""
from __future__ import annotations
import shlex
import sys
from commands import parse_line_and_execute


def run_repl(parser) -> None:
    """REPL loop that uses a provided parser.

    The parser must be created by the caller (main) so we keep a single
    ownership of the grammar and don't reimplement argument parsing here.
    """
    while True:
        try:
            line = input(":>> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        line = line.strip()
        if not line:
            continue

        # Special single-word commands
        if line in ("clear", "cls"):
            import os
            os.system("cls" if os.name == "nt" else "clear")
            continue
        if line in ("quit", "exit", "end"):
            break

        # Use the shared parser to run the command
        parse_line_and_execute(line, parser)


def main() -> None:
    # Convenience when running this file directly: create a parser and run
    from commands import make_parser
    parser = make_parser()
    run_repl(parser)


if __name__ == "__main__":
    main()
