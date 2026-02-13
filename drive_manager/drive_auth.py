from __future__ import print_function
import os
import pickle
from typing import Any
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive']


def authenticate_drive() -> Any:
    """Authenticate with Google Drive using OAuth2 and return an API service.

    This requires a credentials.json file set up by the user with their own
    Google Cloud OAuth 2.0 credentials (BYOC model). See README for setup instructions.

    This will create `token.pickle` after the first successful run.
    """
    creds = None

    # Verify credentials.json exists before attempting authentication
    if not os.path.exists('credentials.json'):
        error_msg = (
            "credentials.json not found.\n"
            "To use Google Drive features, you must set up your own OAuth credentials.\n"
            "See README.md for detailed setup instructions under 'Google Drive Setup (BYOC)'"
        )
        raise FileNotFoundError(error_msg)

    # Load previously saved token if it exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid token, do the OAuth flow
    try:
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the token for next time
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('drive', 'v3', credentials=creds)
        return service
    except FileNotFoundError as e:
        raise
    except Exception as e:
        print(f"Drive authentication failed: {e}")
        raise
