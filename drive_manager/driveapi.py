from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from typing import Any, List, Optional
import os
import io


def upload_file(service: Any, file_path: str, folder_id: Optional[str] = None) -> str:
    """Upload a local file to Google Drive.

    Args:
        service: Authenticated Drive service instance.
        file_path: Path to local file to upload.
        folder_id: Optional Drive folder ID to place the file into.

    Returns:
        The uploaded file's ID on success.
    """
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file_path, mimetype='application/pdf')

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"Uploaded file ID: {file.get('id')}")
        return file.get('id')
    except Exception as e:
        print(f"Upload failed: {e}")
        raise

def find_file_id(service: Any, filename: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
    """Find a file ID by name (optionally within a specific Drive folder)."""
    query = f"name = '{filename}' and trashed = false"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, parents)',
        pageSize=10
    ).execute()

    files = results.get('files', [])
    if not files:
        print(f"No file named '{filename}' found.")
        return None

    # If multiple matches, return the first one
    file = files[0]
    print(f"Found file: {file['name']} (ID: {file['id']})")
    return file['id']


def download_file(service: Any, file_id: str, destination: str) -> None:
    """Download a file by ID into `destination`.

    `destination` may be a full file path or a directory path. If a directory is
    provided, the drive file's name will be used.
    """
    # Resolve destination: if a directory, fetch file name from Drive metadata
    if os.path.isdir(destination):
        meta = service.files().get(fileId=file_id, fields='name').execute()
        filename = meta.get('name')
        destination = os.path.join(destination, filename)

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

    print(f"File saved to {destination}")

def create_folder(service: Any, name: str, parent_id: Optional[str] = None) -> str:
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]

    folder = service.files().create(body=file_metadata, fields='id').execute()
    print(f"Folder created: {folder.get('id')}")
    return folder.get('id')

def share_file(service: Any, file_id: str, role: str = 'reader', anyone: bool = True, email: Optional[str] = None) -> None:
    if anyone:
        user_permission = {
            'type': 'anyone',
            'role': role
        }
    else:
        user_permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }

    service.permissions().create(
        fileId=file_id,
        body=user_permission
    ).execute()

    # Get the shareable link
    file = service.files().get(fileId=file_id, fields='webViewLink').execute()
    print("Shareable link:", file.get('webViewLink'))


# List all top-level folders
# folders = list_folders(service)
# Or list folders inside another folder
# parent_folder_id = "1ABCxyz123..."
# folders = list_folders(service, parent_folder_id)

def list_folders(service: Any, parent_id: Optional[str] = None) -> List[dict]:
    # Define the base query: only folders
    query = "mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields="nextPageToken, files(id, name)",
        pageSize=100
    ).execute()

    folders = results.get('files', [])
    if not folders:
        print("No folders found.")
    else:
        print("Folders:")
        for f in folders:
            print(f"📁 {f['name']} (ID: {f['id']})")

    return folders

def find_folder_by_name(service: Any, folder_name: str) -> Optional[List[dict]]:
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields="files(id, name)"
    ).execute()

    folders = results.get('files', [])
    if folders:
        print(f"Found folder(s) named '{folder_name}':")
        for f in folders:
            print(f"📁 {f['name']} (ID: {f['id']})")
        return folders
    else:
        return None

