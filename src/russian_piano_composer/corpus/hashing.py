"""
File streaming hashing utilities for file-level provenance verification.
"""
import hashlib
from pathlib import Path


def sha256_file(path: Path | str, chunk_size: int = 65536) -> str:
    """
    Compute SHA-256 hex digest of a file by streaming chunks into memory.
    """
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"File not found for SHA-256 computation: {file_path}")

    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()
