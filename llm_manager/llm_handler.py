"""Handle LLM interactions for command generation."""

import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai

from llm_manager.llm_auth import load_llm_credentials, is_llm_available
from llm_manager.llm_formatter import get_command_schema_json


def initialize_llm() -> Optional[Any]:
    """Initialize the LLM (Gemini) with the configured API key.
    
    Returns:
        genai.GenerativeModel instance or None if unavailable.
    """
    if not is_llm_available():
        return None
    
    creds = load_llm_credentials()
    if not creds:
        return None
    
    try:
        genai.configure(api_key=creds['api_key'])
        return genai.GenerativeModel('gemini-pro')
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return None


def ask_llm_for_commands(user_request: str, model: Optional[Any] = None) -> Optional[List[str]]:
    """Send user request to LLM and get suggested commands.
    
    Args:
        user_request: User's natural language request
        model: Initialized LLM model (will be created if not provided)
    
    Returns:
        List of suggested commands, or None if request fails
    """
    if not is_llm_available():
        print("LLM functionality not available. Please set up llm_key.json (see README).")
        return None
    
    if model is None:
        model = initialize_llm()
    
    if model is None:
        print("Failed to initialize LLM. Check your API key configuration.")
        return None
    
    command_schema = get_command_schema_json()
    
    prompt = f"""You are a command generator for a CLI application called 'pdfkitx'. 
Your job is to convert natural language requests into properly formatted commands.

Here is the complete command schema for the application:

{command_schema}

Important rules:
1. Return ONLY the command(s) that should be executed, nothing else
2. Each command should be on its own line
3. Commands must match the syntax exactly as shown in the schema
4. If multiple commands are needed, put each on a separate line
5. Do NOT include any explanation, commentary, or markdown formatting
6. Do NOT wrap commands in code blocks or quotes

User request: {user_request}

Generate the appropriate command(s):"""
    
    try:
        response = model.generate_content(prompt)
        
        if not response.text:
            print("Error: LLM returned empty response")
            return None
        
        # Parse response into individual commands
        commands = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        
        if not commands:
            print("Error: No commands generated from LLM response")
            return None
        
        return commands
    
    except Exception as e:
        print(f"LLM API error: {e}")
        return None


def validate_commands(commands: List[str]) -> tuple[bool, List[str]]:
    """Basic validation of generated commands.
    
    Args:
        commands: List of command strings
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    if not commands:
        errors.append("No commands provided")
        return False, errors
    
    valid_prefixes = ('pdf', 'zip', 'drive', 'help', 'clear', 'exit')
    
    for cmd in commands:
        if not cmd:
            errors.append("Empty command found")
            continue
        
        # Extract the main command (first word)
        parts = cmd.split()
        if not parts:
            errors.append(f"Invalid command: '{cmd}'")
            continue
        
        main_cmd = parts[0].lower()
        
        if main_cmd not in valid_prefixes:
            errors.append(f"Unknown command prefix: '{main_cmd}' in '{cmd}'")
    
    return len(errors) == 0, errors


def format_commands_for_display(commands: List[str]) -> str:
    """Format commands nicely for user review.
    
    Args:
        commands: List of command strings
    
    Returns:
        Formatted string for display
    """
    result = "Generated commands:\n"
    for i, cmd in enumerate(commands, 1):
        result += f"  {i}. {cmd}\n"
    return result
