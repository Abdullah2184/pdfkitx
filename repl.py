"""Improved REPL using the shared argparse parser for consistent parsing.

This REPL will accept the same syntax as the CLI. It uses shlex splitting
so quoted arguments are handled correctly.
"""
from __future__ import annotations
import shlex
import sys
from commands import parse_line_and_execute
from llm_manager.llm_auth import is_llm_available
from llm_manager.llm_handler import (
    ask_llm_for_commands,
    validate_commands,
    format_commands_for_display,
    initialize_llm
)


def run_repl(parser) -> None:
    """REPL loop that uses a provided parser.

    The parser must be created by the caller (main) so we keep a single
    ownership of the grammar and don't reimplement argument parsing here.
    """
    llm_model = None
    if is_llm_available():
        llm_model = initialize_llm()
    
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

        # Check if this is an "llm ask" command
        if line.startswith("llm ask "):
            if llm_model is None:
                print("LLM functionality not available. Check llm_key.json (see README).")
            else:
                request = line[8:].strip()  # Remove "llm ask "
                _handle_llm_ask_interactive(request, parser, llm_model)
            continue

        # Use the shared parser to run the command
        parse_line_and_execute(line, parser)


def _handle_llm_ask_interactive(request: str, parser, llm_model) -> None:
    """Handle 'llm ask' with interactive approval workflow."""
    print("Generating commands...")
    
    commands = ask_llm_for_commands(request, llm_model)
    if not commands:
        print("Failed to generate commands.")
        return
    
    # Validate commands
    is_valid, errors = validate_commands(commands)
    if not is_valid:
        print("⚠️  Validation errors detected:")
        for error in errors:
            print(f"  - {error}")
        print()
    
    # Display commands for approval
    print(format_commands_for_display(commands))
    
    while True:
        response = input("Execute commands? (y)es / (n)o / (m)odify command / (r)egenerate: ").strip().lower()
        
        if response == 'y' or response == 'yes':
            print("Executing commands...")
            for cmd in commands:
                print(f"  > {cmd}")
                parse_line_and_execute(cmd, parser)
            break
        
        elif response == 'n' or response == 'no':
            print("Cancelled.")
            break
        
        elif response == 'm' or response == 'modify':
            cmd_num = input("Command number to modify (1-{}): ".format(len(commands))).strip()
            try:
                idx = int(cmd_num) - 1
                if 0 <= idx < len(commands):
                    modification = input(f"Current: {commands[idx]}\nNew command: ").strip()
                    if modification:
                        commands[idx] = modification
                        print("Modified command. Validating...")
                        is_valid, errors = validate_commands([commands[idx]])
                        if errors:
                            print("  Validation errors:")
                            for error in errors:
                                print(f"    - {error}")
                        else:
                            print("  ✓ Validation passed")
                        print(format_commands_for_display(commands))
                else:
                    print(f"Invalid command number. Please enter 1-{len(commands)}")
            except ValueError:
                print("Invalid input.")
        
        elif response == 'r' or response == 'regenerate':
            specific = input("Regenerate all or for specific command? (all)/(command_num): ").strip().lower()
            if specific == 'all':
                print("Regenerating commands...")
                commands = ask_llm_for_commands(request, llm_model)
                if not commands:
                    print("Failed to regenerate commands.")
                    return
                is_valid, errors = validate_commands(commands)
                if not is_valid:
                    print("⚠️  Validation errors detected:")
                    for error in errors:
                        print(f"  - {error}")
                    print()
                print(format_commands_for_display(commands))
            else:
                try:
                    idx = int(specific) - 1
                    if 0 <= idx < len(commands):
                        print("Regenerating command with more specific context...")
                        specific_request = f"{request}\nSpecifically for: {commands[idx]}"
                        new_cmd = ask_llm_for_commands(specific_request, llm_model)
                        if new_cmd:
                            commands[idx] = new_cmd[0]
                            print("Regenerated command. Updated list:")
                            print(format_commands_for_display(commands))
                        else:
                            print("Failed to regenerate this command.")
                    else:
                        print(f"Invalid command number. Please enter 1-{len(commands)}")
                except ValueError:
                    print("Invalid input.")
        
        else:
            print("Invalid response. Please enter y/n/m/r")


def main() -> None:
    # Convenience when running this file directly: create a parser and run
    from commands import make_parser
    parser = make_parser()
    run_repl(parser)


if __name__ == "__main__":
    main()
