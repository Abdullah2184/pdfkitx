import os
import shelve
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
from typing import Iterable, List, Optional

# Registry shelve that keeps track of created archives and their metadata
REGISTRY_SHELVE = "archives_registry"

def extract_from_zip(zip_path: str, members: Optional[Iterable[str]] = None, target_dir: str = "extracted/") -> Path:
    """
    Extract members (or all) from a ZIP archive into `target_dir`.

    Args:
        zip_path: Path to the zip archive.
        members: Iterable of member filenames to extract. If None, extract all.
        target_dir: Destination directory relative to this module.

    Returns:
        Path to the extraction directory.

    Raises:
        FileNotFoundError: if the zip archive does not exist.
    """
    zip_path = Path(zip_path)
    if not zip_path.is_file():
        raise FileNotFoundError(f"ZIP archive not found: {zip_path}")

    full_dir_path = (Path(__file__).resolve().parent / target_dir)
    full_dir_path.mkdir(parents=True, exist_ok=True)

    with ZipFile(zip_path, "r") as zf:
        if members is None:
            zf.extractall(full_dir_path)
        else:
            for member in members:
                if member not in zf.namelist():
                    print(f"Warning: {member} not found in archive")
                    continue
                zf.extract(member, full_dir_path)

    return full_dir_path

def add_to_zip(zip_path: str, zip_index: str, target: str, file_info: Optional[dict] = None) -> None:
    """
    Add a file or all files in a folder to a ZIP archive and index metadata in a shelve.

    Args:
        zip_path: Archive path (created if missing).
        zip_index: path for shelve index file.
        target: path to a file or directory to add.
        file_info: Optional metadata dictionary to store with the index for each file.

    Raises:
        FileNotFoundError: if target doesn't exist.
    """
    zip_path = Path(zip_path)
    target_path = Path(target)

    if not target_path.exists():
        raise FileNotFoundError(f"Target not found: {target_path}")

    zip_path.parent.mkdir(parents=True, exist_ok=True)

    # determine per-archive index path (use provided zip_index or default to <archive_stem>_index)
    if not zip_index:
        per_index = str(zip_path.with_suffix("") .name + "_index")
    else:
        per_index = zip_index

    # Register the archive in the central registry
    with shelve.open(REGISTRY_SHELVE) as reg:
        entry = reg.get(str(zip_path), {})
        entry.setdefault("index", per_index)
        entry.setdefault("members", [])
        reg[str(zip_path)] = entry

    with ZipFile(zip_path, mode="a", compression=ZIP_DEFLATED) as zf, shelve.open(per_index) as db, shelve.open(REGISTRY_SHELVE) as reg:
        if target_path.is_file():
            arc_name = target_path.name
            zf.write(target_path, arcname=arc_name)
            db[arc_name] = file_info or {}
            # update registry entry
            entry = reg.get(str(zip_path), {})
            if arc_name not in entry.get("members", []):
                entry.setdefault("members", []).append(arc_name)
            reg[str(zip_path)] = entry
        else:
            for file in target_path.rglob("*"):
                if file.is_file():
                    arc_name = str(file.relative_to(target_path))
                    zf.write(file, arcname=arc_name)
                    db[arc_name] = file_info or {}
                    entry = reg.get(str(zip_path), {})
                    if arc_name not in entry.get("members", []):
                        entry.setdefault("members", []).append(arc_name)
                    reg[str(zip_path)] = entry
    
def search_file(zip_index: str, file_info: List[tuple]) -> List[str]:
    """
    Search the shelve index for metadata matching all key/value pairs in file_info.

    Returns a list of matching archive member names.
    """
    matches = []
    with shelve.open(zip_index) as db:
        for key in db:
            meta = db[key] or {}
            found = True
            for option, arg in file_info:
                if meta.get(option) != arg:
                    found = False
                    break
            if found:
                matches.append(key)
    return matches

def remove_from_zip(zip_path: str, zip_index: str, file_name: str) -> None:
    """
    Remove a file from the ZIP archive (and its index entry).

    This safely writes a new archive without the specified member and replaces the original.
    """
    zip_path = Path(zip_path)
    if not zip_path.is_file():
        raise FileNotFoundError(f"ZIP archive not found: {zip_path}")

    temp_fd, temp_name = tempfile.mkstemp(suffix=".zip")
    os.close(temp_fd)

    # determine per-archive index path
    if not zip_index:
        per_index = str(zip_path.with_suffix("").name + "_index")
    else:
        per_index = zip_index

    try:
        with ZipFile(zip_path, "r") as src, ZipFile(temp_name, "w", ZIP_DEFLATED) as dst:
            found = False
            for item in src.infolist():
                if item.filename == file_name:
                    found = True
                    continue
                data = src.read(item.filename)
                dst.writestr(item, data)

        if not found:
            raise KeyError(f"File {file_name} not found in archive")

        os.replace(temp_name, zip_path)

        # Remove from per-archive index and registry if present
        try:
            with shelve.open(per_index) as db:
                if file_name in db:
                    del db[file_name]
        except Exception:
            pass

        # update registry members
        try:
            with shelve.open(REGISTRY_SHELVE) as reg:
                entry = reg.get(str(zip_path), {})
                members = entry.get("members", [])
                if file_name in members:
                    members.remove(file_name)
                    entry["members"] = members
                    reg[str(zip_path)] = entry
        except Exception:
            pass
    finally:
        if os.path.exists(temp_name):
            try:
                os.remove(temp_name)
            except Exception:
                pass

def handle_zip_command(args: List[str]):
    """Parse zip subcommands and dispatch to functions.

    Supported: list, add, remove, extract
    """
    if not args:
        print("No zip subcommand provided.")
        return

    sub = args[0]
    try:
        if sub == "list":
            # No second arg -> list known archives from registry
            if len(args) < 2:
                with shelve.open(REGISTRY_SHELVE) as reg:
                    if not reg:
                        print("No registered archives found.")
                        return
                    for archive, meta in reg.items():
                        members = meta.get("members", [])
                        print(f"{archive} -> {len(members)} members")
                return

            # Otherwise list contents of a specific archive. Prefer registry info if available.
            archive = args[1]
            with shelve.open(REGISTRY_SHELVE) as reg:
                if archive in reg:
                    members = reg[archive].get("members", [])
                    if not members:
                        print(f"{archive} -> (0 members)")
                        return
                    for m in members:
                        print(m)
                    return

            # Fallback: try to open the archive directly
            archive_path = Path(archive)
            if not archive_path.is_file():
                print(f"Archive not found: {archive}")
                return
            with ZipFile(archive_path, "r") as zf:
                for info in zf.infolist():
                    print(info.filename)
        elif sub == "archives":
            # alias for `zip list` with no args (keeps backward compatibility)
            with shelve.open(REGISTRY_SHELVE) as reg:
                if not reg:
                    print("No registered archives found.")
                    return
                for archive, meta in reg.items():
                    members = meta.get("members", [])
                    print(f"{archive} -> {len(members)} members")
        elif sub == "add":
            if len(args) < 3:
                print("Usage: zip add <path> <archive_name>")
                return
            target, archive = args[1], args[2]
            add_to_zip(archive, "zip_index", target)
            print("Added to archive.")
        elif sub == "remove":
            if len(args) < 3:
                print("Usage: zip remove <archive_name> <file>")
                return
            archive, member = args[1], args[2]
            remove_from_zip(archive, "zip_index", member)
            print("Removed from archive.")
        elif sub == "extract":
            if len(args) < 2:
                print("Usage: zip extract <archive_name> [dest] [file1 file2 ...]")
                return
            archive = args[1]
            # remaining args could be dest then members
            if len(args) >= 3:
                dest = args[2]
                members = args[3:] if len(args) > 3 else None
            else:
                dest = "extracted/"
                members = None
            extracted = extract_from_zip(archive, members=members, target_dir=dest)
            print(f"Extracted to {extracted}")
        else:
            print(f"{sub} is not a valid zip command.")
    except Exception as e:
        print(f"ZIP command failed: {e}")