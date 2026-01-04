from pathlib import Path
from typing import Union


def resolve_path(target: Union[str, Path]) -> Path:
    """Resolve and validate a file or folder path.

    Converts relative paths into absolute ones relative to the project and
    raises `FileNotFoundError` if the path does not exist.

    Args:
        target: string or Path to resolve.

    Returns:
        Resolved absolute Path object.
    """
    path = Path(target)

    # Don’t re-resolve if already absolute
    if not path.is_absolute():
        path = (Path(__file__).parent / path).resolve()

    # Existence check
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    return path