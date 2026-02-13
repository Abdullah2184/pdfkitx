"""Load and validate LLM API credentials from llm_key.json."""

import json
import os
from typing import Optional, Dict, Any


def load_llm_credentials() -> Optional[Dict[str, Any]]:
    """Load LLM API credentials from llm_key.json.
    
    Returns:
        Dict with 'provider' and 'api_key' keys, or None if credentials unavailable.
    """
    if not os.path.exists('llm_key.json'):
        return None
    
    try:
        with open('llm_key.json', 'r') as f:
            creds = json.load(f)
        
        # Validate required fields
        if not isinstance(creds, dict):
            print("Error: llm_key.json must contain a JSON object.")
            return None
        
        if 'api_key' not in creds or not creds['api_key']:
            print("Error: llm_key.json must contain 'api_key'.")
            return None
        
        # Check for placeholder values
        if creds['api_key'].startswith('YOUR_'):
            print("Error: Please replace placeholder in llm_key.json with your actual API key.")
            return None
        
        provider = creds.get('provider', 'google')
        return {
            'provider': provider,
            'api_key': creds['api_key']
        }
    
    except json.JSONDecodeError as e:
        print(f"Error: llm_key.json is not valid JSON: {e}")
        return None
    except Exception as e:
        print(f"Error loading llm_key.json: {e}")
        return None


def is_llm_available() -> bool:
    """Check if LLM functionality is available (API key configured)."""
    return load_llm_credentials() is not None
