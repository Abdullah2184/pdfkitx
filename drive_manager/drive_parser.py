from pathlib import Path
import os
from typing import Any, List, Optional
from helper import resolve_path  # have to change this later when resolve_path is moved
from drive_manager.driveapi import (
    upload_file,
    create_folder,
    find_folder_by_name,
    download_file,
    find_file_id,
    share_file,
    list_folders,
)
from drive_manager.drive_auth import authenticate_drive

# Lazy-initialized Drive service to avoid triggering OAuth on import
service: Optional[Any] = None


def get_service() -> Optional[Any]:
    """Return an authenticated Drive service or None if auth fails.
    
    Returns None if Drive service is unavailable, allowing non-Drive
    functionality to continue working normally.
    """
    global service
    if service is None:
        try:
            service = authenticate_drive()
        except FileNotFoundError as e:
            print(f"Drive service unavailable: {e}")
            service = None
        except Exception as e:
            print(f"Failed to authenticate Drive: {e}")
            service = None
    return service


def list_drive_items() -> None:
    """List top-level Drive folders and files (brief)."""
    svc = get_service()
    if svc is None:
        print("Drive service unavailable.")
        return

    # List folders
    try:
        list_folders(svc)
        # Also list some top-level files (non-folder)
        print("Top-level files:")
        results = svc.files().list(q="trashed = false and 'root' in parents", spaces='drive', fields='files(id, name)', pageSize=50).execute()
        files = results.get('files', [])
        if not files:
            print("  (no top-level files found)")
        else:
            for f in files:
                print(f"  - {f['name']} (ID: {f['id']})")
    except Exception as e:
        print(f"Failed to list Drive items: {e}")


def init_drive_session(username: Optional[str] = None) -> None:
    """Force authentication and initialize the Drive session.

    Optionally stores a small username file for convenience.
    """
    global service
    try:
        svc = authenticate_drive()
        service = svc
        print("Drive session initialized.")
        if username:
            try:
                with open('drive_user.txt', 'w') as f:
                    f.write(username)
                print(f"Username saved: {username}")
            except Exception as e:
                print(f"Could not save username: {e}")
    except Exception as e:
        print(f"Failed to initialize Drive session: {e}")


def logout_drive_session() -> None:
    """Forget stored tokens and reset the in-memory service object.

    Removes `token.pickle` so next use requires re-authentication.
    """
    global service
    try:
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
            print('Removed token.pickle; you are now logged out.')
        if os.path.exists('drive_user.txt'):
            os.remove('drive_user.txt')
        service = None
    except Exception as e:
        print(f"Logout failed: {e}")

def handle_drive_command(args):
    if len(args) < 1:
        print("No Drive subcommand provided.")
        return

    subcommand = args[0]

    if subcommand == "list":
        list_drive_items()
    elif subcommand == "init":
        username = args[1] if len(args) > 1 else None
        init_drive_session(username)
    elif subcommand == "logout":
        logout_drive_session()
    elif subcommand == "upload":
        handle_drive_upload(args[1:])
    elif subcommand == "download":
        handle_drive_download(args[1:])
    elif subcommand == "share":
        handle_drive_share(args[1:])
    else:
        print(f"{subcommand} is not a valid Drive command.")

def handle_drive_upload(args):
    if len(args) < 1:
        print("Usage: drive upload <path> [drive_folder]")
        return

    path = Path(args[0])
    drive_folder = args[1] if len(args) > 1 else None

    try:
        svc = get_service()
        if svc is None:
            print("Drive service unavailable.")
            return

        if path.is_file():
            file_path = resolve_path(path)
            if drive_folder and not find_folder_by_name(svc, drive_folder):
                create_folder(svc, drive_folder)
            upload_file(svc, file_path, drive_folder)
        elif path.is_dir():
            dir_path = resolve_path(path)
            for file in dir_path.iterdir():
                if file.is_file():
                    upload_file(svc, file, drive_folder)
        else:
            print(f"Invalid path: {path}")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Upload failed: {e}")

def handle_drive_download(args):
    if len(args) < 1:
        print("Usage: drive download <file_name> [destination_folder]")
        return

    file_name = args[0]
    try:
        svc = get_service()
        if svc is None:
            print("Drive service unavailable.")
            return

        if len(args) > 1:
            dest = Path(args[1])
            dest.mkdir(parents=True, exist_ok=True)
            dest_path = dest
        else:
            dest_path = Path("drive_downloads")
            dest_path.mkdir(parents=True, exist_ok=True)

        file_id = find_file_id(svc, file_name)
        if not file_id:
            print("Sorry, that file doesn't exist.")
            return

        download_file(svc, file_id, str(dest_path))
    except Exception as e:
        print(f"Download failed: {e}")

def handle_drive_share(args):
    if len(args) < 1:
        print("Usage: drive share <file_or_folder> [email]")
        return

    target = args[0]
    try:
        svc = get_service()
        if svc is None:
            print("Drive service unavailable.")
            return

        file_folder_id = find_file_id(svc, target)
        if not file_folder_id:
            print("File or folder not found.")
            return

        if len(args) > 1:
            dest_email = args[1]
            share_file(svc, file_folder_id, role='reader', anyone=False, email=dest_email)
        else:
            share_file(svc, file_folder_id, role='reader', anyone=True)
    except Exception as e:
        print(f"Share failed: {e}")