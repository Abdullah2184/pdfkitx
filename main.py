import sys
from commands import make_parser, execute_args_once
from repl import run_repl


def main(argv: list[str] | None = None) -> int:
    """Single entrypoint for the tool.

    Behavior:
      - No argv or empty argv => start REPL (run_repl)
      - argv present => parse once and execute (execute_args_once)
    """
    args = argv if argv is not None else sys.argv[1:]
    parser = make_parser()

    if not args:
        # interactive mode
        run_repl(parser)
        return 0

    # one-shot mode
    return execute_args_once(parser, args)


if __name__ == "__main__":
    raise SystemExit(main())