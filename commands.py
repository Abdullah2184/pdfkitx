"""Shared command configuration and argparse builder.

This module centralizes CLI/subcommand definitions and attaches adapter
functions that call the existing backend handlers in drive_parser,
zip_parser and pdf_tools. It allows the same parser to be reused by the
CLI, REPL and script runner for consistent behavior.
"""
from __future__ import annotations
import argparse
import shlex
from typing import Callable, List

from drive_manager.drive_parser import handle_drive_command
from zip_manager.zip_parser import handle_zip_command
from pdf_manager.pdf_tools import handle_pdf_command
from help_docs import handle_help_command


def _adapter_call(handler: Callable[[List[str]], None], tokens: List[str]):
    """Helper to call a handler with tokens (skips the top-level command)."""
    # handler expects list[str] starting with subcommand
    handler(tokens)


def make_parser(prog: str = "tool") -> argparse.ArgumentParser:
    """Return a configured argparse.ArgumentParser for the whole tool.

    Each subparser gets set_defaults(func=...) so callers can do:
        ns = parser.parse_args(args)
        ns.func(ns)
    or directly call parser.parse_args(shlex.split(line)).func(ns)
    """
    parser = argparse.ArgumentParser(prog=prog, description="Tool for PDFs, zips and Drive")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # DRIVE
    drive_p = subparsers.add_parser("drive", help="Drive operations")
    drive_sp = drive_p.add_subparsers(dest="sub", required=True)

    d_list = drive_sp.add_parser("list", help="List top-level drive items")
    d_list.set_defaults(func=lambda ns: _adapter_call(handle_drive_command, ["list"]))

    d_init = drive_sp.add_parser("init", help="Initialize drive session")
    d_init.add_argument("username", nargs="?", help="Optional username to save")
    d_init.set_defaults(func=lambda ns: _adapter_call(handle_drive_command, ["init", ns.username] if ns.username else ["init"]))

    d_logout = drive_sp.add_parser("logout", help="Logout and remove tokens")
    d_logout.set_defaults(func=lambda ns: _adapter_call(handle_drive_command, ["logout"]))

    d_upload = drive_sp.add_parser("upload", help="Upload file or folder to Drive")
    d_upload.add_argument("path", help="Path to file or folder")
    d_upload.add_argument("drive_folder", nargs="?", help="Remote folder name")
    d_upload.set_defaults(func=lambda ns: _adapter_call(handle_drive_command, ["upload", ns.path, ns.drive_folder] if ns.drive_folder else ["upload", ns.path]))

    d_download = drive_sp.add_parser("download", help="Download a file from Drive")
    d_download.add_argument("file_name", help="File name to download")
    d_download.add_argument("destination", nargs="?", help="Destination folder")
    d_download.set_defaults(func=lambda ns: _adapter_call(handle_drive_command, ["download", ns.file_name, ns.destination] if ns.destination else ["download", ns.file_name]))

    d_share = drive_sp.add_parser("share", help="Share a file or folder")
    d_share.add_argument("target", help="File or folder name")
    d_share.add_argument("email", nargs="?", help="Optional email to share with")
    d_share.set_defaults(func=lambda ns: _adapter_call(handle_drive_command, ["share", ns.target, ns.email] if ns.email else ["share", ns.target]))

    # ZIP
    zip_p = subparsers.add_parser("zip", help="Zip archive operations")
    zip_sp = zip_p.add_subparsers(dest="sub", required=True)

    z_list = zip_sp.add_parser("list", help="List archives or archive contents")
    z_list.add_argument("archive", nargs="?", help="Archive name to list contents of")
    z_list.set_defaults(func=lambda ns: _adapter_call(handle_zip_command, ["list", ns.archive] if ns.archive else ["list"]))

    z_add = zip_sp.add_parser("add", help="Add file(s) to archive")
    z_add.add_argument("path", help="Path to add")
    z_add.add_argument("archive", help="Archive name")
    z_add.set_defaults(func=lambda ns: _adapter_call(handle_zip_command, ["add", ns.path, ns.archive]))

    z_remove = zip_sp.add_parser("remove", help="Remove a member from an archive")
    z_remove.add_argument("archive", help="Archive name")
    z_remove.add_argument("member", help="Member name to remove")
    z_remove.set_defaults(func=lambda ns: _adapter_call(handle_zip_command, ["remove", ns.archive, ns.member]))

    z_extract = zip_sp.add_parser("extract", help="Extract members from an archive")
    z_extract.add_argument("archive", help="Archive name")
    z_extract.add_argument("dest", nargs="?", default="extracted/", help="Destination directory")
    z_extract.add_argument("members", nargs="*", help="Optional list of members to extract")
    z_extract.set_defaults(func=lambda ns: _adapter_call(handle_zip_command, ["extract", ns.archive, ns.dest] + (ns.members or [])))

    # PDF
    pdf_p = subparsers.add_parser("pdf", help="PDF operations")
    pdf_sp = pdf_p.add_subparsers(dest="sub", required=True)

    p_split = pdf_sp.add_parser("split", help="Split a PDF into ranges")
    p_split.add_argument("file", help="PDF file path")
    p_split.add_argument("ranges", help="Ranges like '1-3,4' (quoted) or single numbers")
    p_split.add_argument("--delete", action="store_true", help="Delete original file after splitting")
    p_split.set_defaults(func=lambda ns: _adapter_call(handle_pdf_command, ["split", ns.file, ns.ranges, "delete"] if ns.delete else ["split", ns.file, ns.ranges]))

    p_merge = pdf_sp.add_parser("merge", help="Merge PDF files")
    p_merge.add_argument("inputs", nargs="+", help="Input pdf files (last one is treated as output if prefixed by --out)")
    p_merge.add_argument("--out", required=True, help="Output merged PDF")
    p_merge.add_argument("--delete", action="store_true", help="Delete originals after merge")
    p_merge.set_defaults(func=lambda ns: _adapter_call(handle_pdf_command, ["merge"] + ns.inputs + [ns.out] + (["delete"] if ns.delete else [])))

    p_extract = pdf_sp.add_parser("extract", help="Extract pages to new file")
    p_extract.add_argument("file", help="Source PDF")
    p_extract.add_argument("pages", help="Pages like '1,3-5'")
    p_extract.add_argument("new", help="Output filename")
    p_extract.set_defaults(func=lambda ns: _adapter_call(handle_pdf_command, ["extract", ns.file, ns.pages, ns.new]))

    p_delete = pdf_sp.add_parser("delete", help="Delete pages from PDF")
    p_delete.add_argument("file", help="Source PDF")
    p_delete.add_argument("pages", help="Pages to delete like '2,5-7'")
    p_delete.add_argument("--replace", action="store_true", help="Replace original file")
    p_delete.set_defaults(func=lambda ns: _adapter_call(handle_pdf_command, ["delete", ns.file, ns.pages, "replace"] if ns.replace else ["delete", ns.file, ns.pages]))

    p_convert = pdf_sp.add_parser("convert", help="Convert files to PDF")
    p_convert.add_argument("inputs", nargs="+", help="Input files or directory")
    p_convert.add_argument("--out", help="Optional output PDF (for combining)")
    p_convert.add_argument("--delete", action="store_true", help="Delete original files")
    p_convert.set_defaults(func=lambda ns: _adapter_call(handle_pdf_command, ["convert"] + ns.inputs + ([ns.out] if ns.out else []) + (["delete"] if ns.delete else [])))

    # HELP passthrough
    help_p = subparsers.add_parser("help", help="Show help topics")
    help_p.add_argument("topic", nargs="*", help="Topic to show")
    help_p.set_defaults(func=lambda ns: _adapter_call(handle_help_command, ns.topic or []))

    # RUN (script runner) - uses the SAME parser when executing lines
    run_p = subparsers.add_parser("run", help="Run commands from a script file")
    run_p.add_argument("script", help="Path to script file")
    run_p.set_defaults(func=handle_run)
    return parser


def execute_args_once(parser: argparse.ArgumentParser, args: List[str]) -> int:
    """Execute a single argv-style invocation against the provided parser.

    Returns an exit code: 0 on success, non-zero on failure. This helper is
    intended for use by `main.py` so `main` does not itself perform parsing.
    """
    try:
        ns = parser.parse_args(args)
        if hasattr(ns, "func"):
            ns.func(ns)
            return 0
        else:
            parser.print_help()
            return 2
    except SystemExit as e:
        # argparse throws SystemExit for parse errors and -h; return code
        return e.code if isinstance(e.code, int) else 1


def handle_run(ns: argparse.Namespace) -> None:
    """Handle the `run <script>` command.

    This opens the provided script file and executes each non-empty,
    non-comment line by parsing it with the SAME grammar (make_parser()).
    Using the same parser guarantees scripts behave exactly like CLI or
    REPL input.
    """
    path = getattr(ns, "script", None)
    if not path:
        print("No script provided")
        return

    try:
        with open(path, "r", encoding="utf-8") as fh:
            script_parser = make_parser()
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parse_line_and_execute(line, script_parser)
    except FileNotFoundError:
        print(f"Script not found: {path}")
    except Exception as exc:  # pragma: no cover - unexpected IO errors
        print(f"Failed to run script {path}: {exc}")


def parse_line_and_execute(line: str, parser: argparse.ArgumentParser) -> None:
    """Parse a single command line string and execute the attached function.

    Prints argparse errors to the console instead of raising.
    """
    try:
        tokens = shlex.split(line)
    except ValueError as e:
        print(f"Failed to parse line: {e}")
        return

    if not tokens:
        return

    try:
        ns = parser.parse_args(tokens)
        if hasattr(ns, "func"):
            ns.func(ns)
        else:
            print("No action for that command.")
    except SystemExit:
        # argparse throws SystemExit on parse errors or -h; capture that
        pass
