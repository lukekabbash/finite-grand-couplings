#!/usr/bin/env python3
"""Write a root-relative SHA-256 drift ledger for this release."""

from __future__ import annotations

from manifest_lib import release_files, release_root, sha256


def main():
    root = release_root()
    entries = [f"{sha256(root / relative)}  {relative.as_posix()}" for relative in release_files(root)]
    manifest = root / "MANIFEST.sha256"
    manifest.write_text("\n".join(entries) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {manifest} ({len(entries)} files)")


if __name__ == "__main__":
    main()

