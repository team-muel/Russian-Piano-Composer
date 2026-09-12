import hashlib
from pathlib import Path

import pytest

from russian_piano_composer.corpus.hashing import sha256_file


def test_sha256_file_valid(tmp_path: Path):
    content = b"Russian Piano Composer RC-006 test artifact content."
    expected_hash = hashlib.sha256(content).hexdigest()

    test_file = tmp_path / "test_artifact.bin"
    test_file.write_bytes(content)

    actual_hash = sha256_file(test_file)
    assert actual_hash == expected_hash


def test_sha256_file_missing():
    with pytest.raises(FileNotFoundError, match="File not found"):
        sha256_file("non_existent_file_path_12345.dat")
