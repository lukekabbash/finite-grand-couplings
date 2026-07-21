#!/usr/bin/env python3
"""Canonical file selection and hashing for the release manifest."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


EXCLUDED_DIRECTORIES = {".git", "__pycache__", ".pytest_cache", "tmp"}
EXCLUDED_FILES = {".DS_Store", "MANIFEST.sha256"}


def release_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_transient_file(relative: Path) -> bool:
    return (
        relative.name in EXCLUDED_FILES
        or relative.suffix == ".pyc"
        or (
            relative.parts[:1] == ("results",)
            and relative.name.startswith("latest-")
            and relative.suffix == ".log"
        )
    )


def release_files(root: Path):
    for directory, names, files in os.walk(root, topdown=True, followlinks=False):
        directory_path = Path(directory)
        kept_names = []
        for name in names:
            candidate = directory_path / name
            if name in EXCLUDED_DIRECTORIES:
                continue
            if candidate.is_symlink():
                raise ValueError(f"release directory may not be a symlink: {candidate}")
            kept_names.append(name)
        names[:] = sorted(kept_names)

        for name in sorted(files):
            path = directory_path / name
            relative = path.relative_to(root)
            if is_transient_file(relative):
                continue
            if path.is_symlink():
                raise ValueError(f"release file may not be a symlink: {path}")
            if path.is_file():
                yield relative


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

