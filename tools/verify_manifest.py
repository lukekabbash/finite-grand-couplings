#!/usr/bin/env python3
"""Fail closed when a release file is missing, extra, unsafe, or changed."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from manifest_lib import release_files, release_root, sha256


HASH_PATTERN = re.compile(r"[0-9a-f]{64}")


def parse_manifest(path: Path) -> dict[Path, str]:
    entries: dict[Path, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            raise ValueError(f"blank manifest line at {line_number}")
        try:
            digest, raw_path = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"malformed manifest line {line_number}") from error
        if not HASH_PATTERN.fullmatch(digest):
            raise ValueError(f"invalid SHA-256 on manifest line {line_number}")
        pure = PurePosixPath(raw_path)
        if pure.is_absolute() or not pure.parts or ".." in pure.parts or "." in pure.parts:
            raise ValueError(f"unsafe path on manifest line {line_number}: {raw_path}")
        relative = Path(*pure.parts)
        if relative in entries:
            raise ValueError(f"duplicate path on manifest line {line_number}: {raw_path}")
        entries[relative] = digest
    return entries


def main():
    root = release_root()
    manifest_path = root / "MANIFEST.sha256"
    if not manifest_path.is_file():
        raise SystemExit("MANIFEST.sha256 is missing; run tools/make_manifest.py intentionally")

    expected = parse_manifest(manifest_path)
    actual_paths = set(release_files(root))
    expected_paths = set(expected)
    if actual_paths != expected_paths:
        missing = sorted(expected_paths - actual_paths)
        extra = sorted(actual_paths - expected_paths)
        if missing:
            print("missing release files:")
            for path in missing:
                print(f"  {path.as_posix()}")
        if extra:
            print("unsealed release files:")
            for path in extra:
                print(f"  {path.as_posix()}")
        raise SystemExit(1)

    changed = [path for path, digest in expected.items() if sha256(root / path) != digest]
    if changed:
        print("changed release files:")
        for path in sorted(changed):
            print(f"  {path.as_posix()}")
        raise SystemExit(1)

    print(f"manifest verification: PASS ({len(expected)} files)")


if __name__ == "__main__":
    main()

